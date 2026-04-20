from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.types import Message

from config import config
from database import queries

router = Router()


@router.message(F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}))
async def handle_group_message(message: Message) -> None:
    if not message.from_user:
        return

    chat = message.chat
    user = message.from_user

    await queries.upsert_chat(
        chat_id=chat.id,
        title=chat.title or "",
        username=getattr(chat, "username", None),
        chat_type=chat.type,
    )

    is_operator = int(user.id in config.operator_ids)

    await queries.insert_message(
        chat_id=chat.id,
        message_id=message.message_id,
        user_id=user.id,
        username=user.username,
        full_name=user.full_name,
        is_operator=is_operator,
        text=message.text or message.caption,
        date_iso=message.date.isoformat(),
    )
