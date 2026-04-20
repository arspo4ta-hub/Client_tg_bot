# Client TG Bot — Telegram Analytics Bot

Бот мониторит переписку в группах/супергруппах и каждый понедельник в 09:00 отправляет аналитический отчёт владельцу.

## Что собирает

- Количество сообщений по каждому чату (с динамикой +/- vs прошлая неделя)
- Топ активных клиентов
- Среднее время ответа операторов
- Топ ключевых слов за неделю

## Требования

- Python 3.11+
- Аккаунт бота от [@BotFather](https://t.me/BotFather)

## Установка

```bash
git clone ...
cd Client_tg_bot
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Настройка

```bash
cp .env.example .env
```

Заполните `.env`:

| Переменная | Описание |
|---|---|
| `BOT_TOKEN` | Токен от @BotFather |
| `OWNER_ID` | Ваш Telegram user_id (получить через @userinfobot) |
| `OPERATOR_IDS` | Через запятую user_id сотрудников (для расчёта времени ответа) |
| `DATABASE_PATH` | Путь к файлу SQLite (по умолчанию `analytics.db`) |
| `REPORT_TIMEZONE` | Часовой пояс для отчёта, например `Europe/Moscow` |
| `LOG_LEVEL` | `INFO` или `DEBUG` |

## Настройка бота в Telegram

Чтобы бот читал все сообщения в группах — **один из двух вариантов**:

**Вариант 1 (рекомендуется):** Добавьте бота в группу как **администратора**.

**Вариант 2:** Отключите privacy mode в @BotFather:
```
/mybots → выберите бота → Bot Settings → Group Privacy → Turn off
```

## Запуск

```bash
python main.py
```

## Команды (в личном чате с ботом)

| Команда | Описание |
|---|---|
| `/report` | Получить отчёт прямо сейчас |
| `/chats` | Список всех мониторируемых чатов |
| `/stats` | Быстрая сводка по всем данным |

Команды работают только для `OWNER_ID` — остальные пользователи ответа не получают.

## Структура проекта

```
├── main.py              # Точка входа
├── config.py            # Конфигурация из .env
├── scheduler.py         # Еженедельное задание
├── database/
│   ├── db.py            # Инициализация SQLite
│   └── queries.py       # Все SQL-запросы
├── handlers/
│   ├── messages.py      # Сохранение входящих сообщений
│   └── admin.py         # Команды владельца
└── analytics/
    ├── collector.py     # Вычисление аналитики
    └── report.py        # Форматирование отчёта
```
