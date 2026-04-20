import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import config
from database.db import init_db, close_db
from handlers.messages import router as messages_router
from handlers.admin import router as admin_router
from scheduler import setup_scheduler


async def main() -> None:
    logging.basicConfig(
        level=getattr(logging, config.log_level),
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )

    await init_db(config.database_path)

    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    dp.include_router(messages_router)
    dp.include_router(admin_router)

    scheduler = setup_scheduler(bot)
    scheduler.start()

    try:
        await dp.start_polling(bot, allowed_updates=["message"])
    finally:
        scheduler.shutdown(wait=False)
        await close_db()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
