import datetime

from analytics.collector import WeeklyReportData

_MD_SPECIAL = r"\_*[]()~`>#+-=|{}.!"


def escape_md(text: str) -> str:
    for ch in _MD_SPECIAL:
        text = text.replace(ch, f"\\{ch}")
    return text


def _format_delta(delta_pct: float | None) -> str:
    if delta_pct is None:
        return "🆕"
    if delta_pct > 0:
        return f"📈 \\+{delta_pct:.0f}%"
    if delta_pct < 0:
        return f"📉 {delta_pct:.0f}%"
    return "➡️ 0%"


def _fmt_seconds(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.0f} сек"
    if seconds < 3600:
        return f"{seconds / 60:.1f} мин"
    return f"{seconds / 3600:.1f} ч"


def format_report(data: WeeklyReportData) -> str:
    w_start = data.week_start.strftime("%d\\.%m\\.%Y")
    w_end = data.week_end.strftime("%d\\.%m\\.%Y")

    lines = [
        "📊 *Еженедельный отчёт*",
        f"📅 {w_start} — {w_end}",
        f"💬 Всего сообщений: *{data.total_messages}*",
        f"🗂 Активных чатов: *{data.total_chats_active}*",
        "",
    ]

    # Section 1: Message counts per chat
    lines.append("━━━━━━━━━━━━━━━━━━━")
    lines.append("*1\\. Активность по чатам*")
    if data.message_counts:
        for i, chat in enumerate(data.message_counts[:20], 1):
            delta_str = _format_delta(chat["delta_pct"])
            title = escape_md(chat["title"] or "Без названия")
            lines.append(f"{i}\\. {title}: *{chat['count']}* {delta_str}")
    else:
        lines.append("_Нет данных_")
    lines.append("")

    # Section 2: Top active users
    lines.append("━━━━━━━━━━━━━━━━━━━")
    lines.append("*2\\. Топ активных клиентов*")
    if data.top_users:
        for i, user in enumerate(data.top_users[:10], 1):
            name = escape_md(user.get("full_name") or user.get("username") or "Unknown")
            lines.append(f"{i}\\. {name}: *{user['msg_count']}* сообщений")
    else:
        lines.append("_Нет данных_")
    lines.append("")

    # Section 3: Response times
    lines.append("━━━━━━━━━━━━━━━━━━━")
    lines.append("*3\\. Среднее время ответа операторов*")
    if data.response_times:
        for rt in data.response_times[:15]:
            title = escape_md(rt["title"] or "Без названия")
            avg_fmt = escape_md(_fmt_seconds(rt["avg_seconds"]))
            lines.append(f"• {title}: *{avg_fmt}*")
    else:
        lines.append("_Нет данных \\(нет настроенных операторов или ответов\\)_")
    lines.append("")

    # Section 4: Keywords
    lines.append("━━━━━━━━━━━━━━━━━━━")
    lines.append("*4\\. Топ ключевых слов*")
    if data.top_keywords:
        parts = [f"`{escape_md(w)}`×{c}" for w, c in data.top_keywords]
        lines.append(" ".join(parts))
    else:
        lines.append("_Нет данных_")

    return "\n".join(lines)
