#!/bin/bash
# Следит за изменениями в GitHub и перезапускает бота автоматически

BRANCH="main"
CHECK_INTERVAL=60  # секунд между проверками
BOT_PID=""
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() { echo -e "[$(date '+%H:%M:%S')] $1"; }

start_bot() {
    source "$SCRIPT_DIR/venv/bin/activate" 2>/dev/null || true
    cd "$SCRIPT_DIR"
    python main.py &
    BOT_PID=$!
    log "${GREEN}✓ Бот запущен (PID $BOT_PID)${NC}"
}

stop_bot() {
    if [ -n "$BOT_PID" ] && kill -0 "$BOT_PID" 2>/dev/null; then
        kill "$BOT_PID"
        wait "$BOT_PID" 2>/dev/null
        log "${YELLOW}⏹ Бот остановлен${NC}"
    fi
}

install_deps() {
    source "$SCRIPT_DIR/venv/bin/activate" 2>/dev/null || true
    pip install -q -r "$SCRIPT_DIR/requirements.txt"
}

# Обработка Ctrl+C
trap 'log "${RED}Остановка...${NC}"; stop_bot; exit 0' SIGINT SIGTERM

# Первоначальная проверка
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    log "${RED}Ошибка: файл .env не найден. Создайте его из .env.example${NC}"
    exit 1
fi

cd "$SCRIPT_DIR"

# Создаём venv если нет
if [ ! -d "venv" ]; then
    log "Создаём виртуальное окружение..."
    python3 -m venv venv
    install_deps
fi

log "Запускаем бота..."
start_bot
log "Слежу за обновлениями каждые ${CHECK_INTERVAL} сек. Ctrl+C для остановки."
echo ""

while true; do
    sleep "$CHECK_INTERVAL"

    # Получаем изменения
    git fetch origin "$BRANCH" --quiet 2>/dev/null

    LOCAL=$(git rev-parse HEAD 2>/dev/null)
    REMOTE=$(git rev-parse "origin/$BRANCH" 2>/dev/null)

    if [ "$LOCAL" != "$REMOTE" ]; then
        COMMIT_MSG=$(git log --oneline "HEAD..origin/$BRANCH" 2>/dev/null | head -3)
        log "${YELLOW}🔄 Обнаружены изменения:${NC}"
        echo "$COMMIT_MSG"

        stop_bot
        git pull origin "$BRANCH" --quiet
        install_deps
        start_bot
        log "${GREEN}✓ Обновление применено${NC}"
        echo ""
    fi

    # Перезапускаем бота если он упал
    if ! kill -0 "$BOT_PID" 2>/dev/null; then
        log "${YELLOW}⚠ Бот упал, перезапускаем...${NC}"
        start_bot
    fi
done
