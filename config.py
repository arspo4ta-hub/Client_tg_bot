from dataclasses import dataclass
from dotenv import load_dotenv
import os

load_dotenv()


@dataclass(frozen=True)
class Config:
    bot_token: str
    owner_id: int
    operator_ids: frozenset
    database_path: str
    report_timezone: str
    log_level: str


def _load_config() -> Config:
    token = os.environ["BOT_TOKEN"]
    owner_id = int(os.environ["OWNER_ID"])
    raw_ops = os.getenv("OPERATOR_IDS", "")
    operator_ids = frozenset(
        int(x.strip()) for x in raw_ops.split(",") if x.strip()
    )
    return Config(
        bot_token=token,
        owner_id=owner_id,
        operator_ids=operator_ids,
        database_path=os.getenv("DATABASE_PATH", "analytics.db"),
        report_timezone=os.getenv("REPORT_TIMEZONE", "Europe/Moscow"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )


config = _load_config()
