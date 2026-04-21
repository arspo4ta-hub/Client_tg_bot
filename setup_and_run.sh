#!/bin/bash
set -e

echo "=== Установка Telegram Analytics Bot ==="

# Проверяем Python
if ! command -v python3 &>/dev/null; then
    echo "ОШИБКА: Python3 не найден. Установите с https://python.org"
    exit 1
fi

PYTHON=$(command -v python3.11 || command -v python3 || command -v python)
echo "Python: $($PYTHON --version)"

# Создаём виртуальное окружение
echo "Создаём виртуальное окружение..."
$PYTHON -m venv venv
source venv/bin/activate

# Устанавливаем зависимости
echo "Устанавливаем зависимости..."
pip install -q -r requirements.txt

# Создаём .env если нет
if [ ! -f .env ]; then
    cp .env.example .env
    echo ""
    echo "ВАЖНО: Откройте файл .env и заполните:"
    echo "  BOT_TOKEN=  (токен от @BotFather)"
    echo "  OWNER_ID=   (ваш Telegram user_id)"
    echo ""
    read -p "Нажмите Enter после заполнения .env..."
fi

# Проверяем .env
if grep -q "your_bot_token_here" .env 2>/dev/null; then
    echo "ОШИБКА: Заполните BOT_TOKEN в файле .env"
    exit 1
fi

echo ""
echo "=== Запускаем бота ==="
$PYTHON main.py
