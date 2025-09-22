#!/bin/bash

# Скрипт для быстрого перезапуска бота на сервере
# Использование: ./restart_bot.sh

set -e

# Конфигурация
SERVER_HOST="147.45.143.18"
SERVER_USER="root"
SCREEN_NAME="price_parser_bot"

echo "🔄 Перезапускаем бота на сервере $SERVER_HOST..."

ssh $SERVER_USER@$SERVER_HOST << EOF
    echo "🛑 Останавливаем все процессы бота..."
    # Убиваем screen сессию
    screen -S $SCREEN_NAME -X quit 2>/dev/null || echo "Screen не был запущен"
    
    # Убиваем все процессы python bot/main.py принудительно
    pkill -f "python bot/main.py" 2>/dev/null || echo "Процессы не найдены"
    
    # Ждем 2 секунды для завершения процессов
    sleep 2
    
    echo "🤖 Запускаем бота заново..."
    screen -dmS $SCREEN_NAME bash -c "cd /root/PriceParcer && source venv/bin/activate && python bot/main.py"
    
    echo "✅ Бот перезапущен в screen '$SCREEN_NAME'"
    echo "Для просмотра логов используйте: screen -r $SCREEN_NAME"
EOF

echo "🎉 Бот успешно перезапущен!"
