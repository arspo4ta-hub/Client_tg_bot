import logging
from aiogram import Router
from aiogram import F
from aiogram.enums import ChatType
from aiogram.filters import Command
from aiogram.types import Message

from config import config
from database import queries
from analytics.collector import generate_report_data
from analytics.report import format_report, escape_md

logger = logging.getLogger(__name__)
router = Router()


def _is_owner(message: Message) -> bool:
    return bool(message.from_user and message.from_user.id == config.owner_id)


@router.message(Command("report"), F.chat.type == ChatType.PRIVATE)
async def cmd_report(message: Message) -> None:
    if not _is_owner(message):
        return
    await message.answer("Генерирую отчёт...")
    try:
        data = await generate_report_data()
        text = format_report(data)
        await message.answer(text, parse_mode="MarkdownV2")
    except Exception:
        logger.exception("Failed to generate report")
        await message.answer("Ошибка при генерации отчёта. Проверьте логи.")


@router.message(Command("chats"), F.chat.type == ChatType.PRIVATE)
async def cmd_chats(message: Message) -> None:
    if not _is_owner(message):
        return
    rows = await queries.get_all_chats()
    if not rows:
        await message.answer("Чатов пока нет\\. Добавьте бота в группы\\.", parse_mode="MarkdownV2")
        return
    lines = []
    for r in rows:
        title = escape_md(r["title"] or "Без названия")
        cid = str(r["chat_id"])
        lines.append(f"• *{title}* \\(`{cid}`\\)")
    await message.answer("\n".join(lines), parse_mode="MarkdownV2")


@router.message(Command("stats"), F.chat.type == ChatType.PRIVATE)
async def cmd_stats(message: Message) -> None:
    if not _is_owner(message):
        return
    stats = await queries.get_quick_stats()
    text = (
        f"📊 *Быстрая статистика*\n\n"
        f"💬 Всего сообщений: *{stats['total_messages']}*\n"
        f"🗂 Всего чатов: *{stats['total_chats']}*\n"
        f"📅 За последние 7 дней: *{stats['week_messages']}*"
    )
    await message.answer(text, parse_mode="MarkdownV2")
