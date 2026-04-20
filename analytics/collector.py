import datetime
import re
from collections import Counter
from dataclasses import dataclass, field

from database import queries

_RUSSIAN_STOP_WORDS = frozenset({
    "и", "в", "на", "что", "это", "как", "по", "но", "не", "из",
    "он", "она", "они", "мы", "вы", "я", "то", "так", "же", "от",
    "до", "у", "за", "при", "со", "или", "бы", "есть", "уже",
    "все", "для", "к", "с", "а", "о", "об", "да", "нет", "там",
    "тут", "вот", "мне", "тебе", "нас", "вас", "был", "была",
    "были", "быть", "буду", "будет", "будут", "если", "чтобы",
    "когда", "тоже", "только", "еще", "уже", "очень", "можно",
    "нужно", "надо", "этот", "эта", "эти", "того", "этого",
})


@dataclass
class WeeklyReportData:
    week_start: datetime.date
    week_end: datetime.date
    message_counts: list = field(default_factory=list)
    top_users: list = field(default_factory=list)
    response_times: list = field(default_factory=list)
    top_keywords: list = field(default_factory=list)
    total_messages: int = 0
    total_chats_active: int = 0


def _extract_keywords(texts: list[str], top_n: int = 15) -> list[tuple]:
    counter: Counter = Counter()
    for text in texts:
        if not text:
            continue
        words = re.findall(r"[а-яёa-z]{4,}", text.lower())
        counter.update(w for w in words if w not in _RUSSIAN_STOP_WORDS)
    return counter.most_common(top_n)


async def generate_report_data(
    reference_date: datetime.date | None = None,
) -> WeeklyReportData:
    today = reference_date or datetime.date.today()
    # Report always covers the previous Mon–Sun
    days_since_monday = today.weekday()
    week_end = today - datetime.timedelta(days=days_since_monday)
    week_start = week_end - datetime.timedelta(days=7)
    prev_start = week_start - datetime.timedelta(days=7)

    ws = week_start.isoformat()
    we = week_end.isoformat()
    ps = prev_start.isoformat()

    counts = await queries.get_weekly_message_counts(ws, we)
    prev_counts = await queries.get_weekly_message_counts(ps, ws)
    chat_titles = await queries.get_chat_titles()
    top_users = await queries.get_top_active_users(ws, we)
    response_times_raw = await queries.get_response_times(ws, we)
    texts = await queries.get_all_message_texts(ws, we)

    prev_map = {row["chat_id"]: row["count"] for row in prev_counts}
    message_counts = []
    for row in counts:
        cid = row["chat_id"]
        cur = row["count"]
        prev = prev_map.get(cid, 0)
        delta = ((cur - prev) / prev * 100) if prev else None
        message_counts.append({
            "chat_id": cid,
            "title": chat_titles.get(cid, str(cid)),
            "count": cur,
            "prev_count": prev,
            "delta_pct": delta,
        })

    response_times = [
        {
            "chat_id": row["chat_id"],
            "title": chat_titles.get(row["chat_id"], str(row["chat_id"])),
            "avg_seconds": row["avg_seconds"],
        }
        for row in response_times_raw
        if row["avg_seconds"] is not None
    ]

    top_keywords = _extract_keywords(texts)

    return WeeklyReportData(
        week_start=week_start,
        week_end=week_end - datetime.timedelta(days=1),
        message_counts=message_counts,
        top_users=[dict(row) for row in top_users],
        response_times=response_times,
        top_keywords=top_keywords,
        total_messages=sum(r["count"] for r in message_counts),
        total_chats_active=len(message_counts),
    )
