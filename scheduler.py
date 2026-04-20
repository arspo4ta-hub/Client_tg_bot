import logging

import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from config import config
from analytics.collector import generate_report_data
from analytics.report import format_report

logger = logging.getLogger(__name__)


def setup_scheduler(bot) -> AsyncIOScheduler:
    tz = pytz.timezone(config.report_timezone)
    scheduler = AsyncIOScheduler(timezone=tz)
    scheduler.add_job(
        func=_send_weekly_report,
        trigger=CronTrigger(day_of_week="mon", hour=9, minute=0, timezone=tz),
        args=[bot],
        id="weekly_report",
        name="Weekly Analytics Report",
        replace_existing=True,
        misfire_grace_time=3600,
    )
    return scheduler


async def _send_weekly_report(bot) -> None:
    logger.info("Generating weekly report...")
    try:
        data = await generate_report_data()
        text = format_report(data)
        await bot.send_message(
            chat_id=config.owner_id,
            text=text,
            parse_mode="MarkdownV2",
        )
        logger.info("Weekly report sent to owner %s", config.owner_id)
    except Exception:
        logger.exception("Failed to send weekly report")
