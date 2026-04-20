import datetime
from database.db import get_db


async def upsert_chat(
    chat_id: int, title: str, username: str | None, chat_type: str
) -> None:
    db = await get_db()
    now = datetime.datetime.utcnow().isoformat()
    await db.execute(
        """
        INSERT INTO chats(chat_id, title, username, chat_type, first_seen, last_seen)
        VALUES(?, ?, ?, ?, ?, ?)
        ON CONFLICT(chat_id) DO UPDATE SET
            title=excluded.title,
            username=excluded.username,
            last_seen=excluded.last_seen
        """,
        (chat_id, title, username, chat_type, now, now),
    )
    await db.commit()


async def insert_message(
    chat_id: int,
    message_id: int,
    user_id: int,
    username: str | None,
    full_name: str | None,
    is_operator: int,
    text: str | None,
    date_iso: str,
) -> None:
    db = await get_db()
    await db.execute(
        """
        INSERT OR IGNORE INTO messages
            (chat_id, message_id, user_id, username, full_name, is_operator, text, date)
        VALUES(?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (chat_id, message_id, user_id, username, full_name, is_operator, text, date_iso),
    )
    await db.commit()


async def get_weekly_message_counts(week_start: str, week_end: str) -> list:
    db = await get_db()
    async with db.execute(
        """
        SELECT chat_id, COUNT(*) as count
        FROM messages
        WHERE date >= ? AND date < ?
        GROUP BY chat_id
        ORDER BY count DESC
        """,
        (week_start, week_end),
    ) as cursor:
        return await cursor.fetchall()


async def get_top_active_users(week_start: str, week_end: str, limit: int = 10) -> list:
    db = await get_db()
    async with db.execute(
        """
        SELECT user_id, full_name, username, COUNT(*) as msg_count
        FROM messages
        WHERE is_operator = 0 AND date >= ? AND date < ?
        GROUP BY user_id
        ORDER BY msg_count DESC
        LIMIT ?
        """,
        (week_start, week_end, limit),
    ) as cursor:
        return await cursor.fetchall()


async def get_response_times(week_start: str, week_end: str) -> list:
    db = await get_db()
    async with db.execute(
        """
        SELECT
            cl.chat_id,
            AVG((julianday(op.date) - julianday(cl.date)) * 86400) AS avg_seconds
        FROM messages cl
        JOIN messages op ON (
            op.chat_id = cl.chat_id
            AND op.is_operator = 1
            AND op.date > cl.date
            AND op.date <= datetime(cl.date, '+24 hours')
            AND op.date = (
                SELECT MIN(date) FROM messages
                WHERE chat_id = cl.chat_id
                  AND is_operator = 1
                  AND date > cl.date
            )
        )
        WHERE cl.is_operator = 0
          AND cl.date >= ?
          AND cl.date < ?
        GROUP BY cl.chat_id
        """,
        (week_start, week_end),
    ) as cursor:
        return await cursor.fetchall()


async def get_all_message_texts(week_start: str, week_end: str) -> list[str]:
    db = await get_db()
    async with db.execute(
        """
        SELECT text FROM messages
        WHERE text IS NOT NULL AND date >= ? AND date < ?
        """,
        (week_start, week_end),
    ) as cursor:
        rows = await cursor.fetchall()
    return [row["text"] for row in rows if row["text"]]


async def get_chat_titles() -> dict:
    db = await get_db()
    async with db.execute("SELECT chat_id, title FROM chats") as cursor:
        rows = await cursor.fetchall()
    return {row["chat_id"]: row["title"] for row in rows}


async def get_all_chats() -> list:
    db = await get_db()
    async with db.execute(
        "SELECT chat_id, title, username, last_seen FROM chats ORDER BY last_seen DESC"
    ) as cursor:
        return await cursor.fetchall()


async def get_quick_stats() -> dict:
    db = await get_db()
    week_start = (
        datetime.datetime.utcnow() - datetime.timedelta(days=7)
    ).isoformat()
    async with db.execute("SELECT COUNT(*) as total FROM messages") as cur:
        total = (await cur.fetchone())["total"]
    async with db.execute("SELECT COUNT(*) as total FROM chats") as cur:
        total_chats = (await cur.fetchone())["total"]
    async with db.execute(
        "SELECT COUNT(*) as total FROM messages WHERE date >= ?", (week_start,)
    ) as cur:
        week_total = (await cur.fetchone())["total"]
    return {
        "total_messages": total,
        "total_chats": total_chats,
        "week_messages": week_total,
    }
