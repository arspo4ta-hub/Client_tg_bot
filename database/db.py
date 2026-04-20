import aiosqlite

_conn: aiosqlite.Connection | None = None

_SCHEMA = """
CREATE TABLE IF NOT EXISTS chats (
    chat_id    INTEGER PRIMARY KEY,
    title      TEXT,
    username   TEXT,
    chat_type  TEXT,
    first_seen TEXT NOT NULL,
    last_seen  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS messages (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id     INTEGER NOT NULL REFERENCES chats(chat_id),
    message_id  INTEGER NOT NULL,
    user_id     INTEGER NOT NULL,
    username    TEXT,
    full_name   TEXT,
    is_operator INTEGER NOT NULL DEFAULT 0,
    text        TEXT,
    date        TEXT NOT NULL,
    UNIQUE(chat_id, message_id)
);

CREATE INDEX IF NOT EXISTS idx_messages_chat_date ON messages(chat_id, date);
CREATE INDEX IF NOT EXISTS idx_messages_date ON messages(date);
"""


async def init_db(path: str) -> None:
    global _conn
    _conn = await aiosqlite.connect(path)
    _conn.row_factory = aiosqlite.Row
    await _conn.execute("PRAGMA journal_mode=WAL")
    await _conn.execute("PRAGMA foreign_keys=ON")
    await _conn.executescript(_SCHEMA)
    await _conn.commit()


async def get_db() -> aiosqlite.Connection:
    if _conn is None:
        raise RuntimeError("Database not initialised. Call init_db() first.")
    return _conn


async def close_db() -> None:
    if _conn is not None:
        await _conn.close()
