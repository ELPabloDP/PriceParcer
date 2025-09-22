#!/bin/bash

# Скрипт для просмотра логов бота
# Использование: ./logs.sh

# Конфигурация
SERVER_HOST="147.45.143.18"
SERVER_USER="root"
SCREEN_NAME="price_parser_bot"

echo "📋 Подключаемся к логам бота на сервере $SERVER_HOST..."
echo "Для выхода из screen используйте: Ctrl+A, затем D"
echo ""

ssh -t $SERVER_USER@$SERVER_HOST "screen -r $SCREEN_NAME"
