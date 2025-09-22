#!/bin/bash

# Скрипт для редактирования .env файла на сервере
# Использование: ./edit_env.sh

# Конфигурация
SERVER_HOST="147.45.143.18"
SERVER_USER="root"

echo "📝 Редактируем .env файл на сервере $SERVER_HOST..."
echo "Для выхода из редактора используйте: Ctrl+X, затем Y, затем Enter"
echo ""

ssh -t $SERVER_USER@$SERVER_HOST "cd /root/PriceParcer && nano .env"
