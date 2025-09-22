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
    echo "🛑 Останавливаем существующий бот..."
    screen -S $SCREEN_NAME -X quit 2>/dev/null || echo "Бот не был запущен"
    
    echo "🤖 Запускаем бота заново..."
    screen -dmS $SCREEN_NAME bash -c "cd /root/PriceParcer && source venv/bin/activate && python bot/main.py"
    
    echo "✅ Бот перезапущен в screen '$SCREEN_NAME'"
    echo "Для просмотра логов используйте: screen -r $SCREEN_NAME"
EOF

echo "🎉 Бот успешно перезапущен!"
