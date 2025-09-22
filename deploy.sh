#!/bin/bash

# Скрипт для деплоя проекта на сервер
# Использование: ./deploy.sh

set -e

# Конфигурация
SERVER_HOST="147.45.143.18"
SERVER_USER="root"
PROJECT_NAME="PriceParcer"
REMOTE_PATH="/root/$PROJECT_NAME"
SCREEN_NAME="price_parser_bot"

echo "🚀 Начинаем деплой проекта $PROJECT_NAME на сервер $SERVER_HOST"

# 1. Коммитим и пушим изменения в Git
echo "📝 Коммитим изменения в Git..."
git add .
git commit -m "Deploy: $(date '+%Y-%m-%d %H:%M:%S')" || echo "Нет изменений для коммита"
git push origin main

# 2. Подключаемся к серверу и обновляем код
echo "🔄 Обновляем код на сервере..."
ssh $SERVER_USER@$SERVER_HOST << EOF
    # Создаем директорию проекта если её нет
    mkdir -p $REMOTE_PATH
    
    # Клонируем или обновляем репозиторий
    if [ -d "$REMOTE_PATH/.git" ]; then
        echo "Обновляем существующий репозиторий..."
        cd $REMOTE_PATH
        git pull origin main
    else
        echo "Клонируем репозиторий..."
        rm -rf $REMOTE_PATH
        git clone https://github.com/ELPabloDP/PriceParcer.git $REMOTE_PATH
    fi
    
    # Устанавливаем зависимости
    echo "📦 Устанавливаем зависимости..."
    cd $REMOTE_PATH
    apt update
    apt install -y python3 python3-pip python3-venv
    
    # Создаем виртуальное окружение
    python3 -m venv venv
    source venv/bin/activate
    
    # Устанавливаем Python пакеты
    pip install -r requirements.txt
    
    # Создаем необходимые директории
    mkdir -p logs
    
    # Выполняем миграции Django
    echo "🗄️ Выполняем миграции базы данных..."
    python manage.py migrate
    
    # Создаем .env файл если его нет
    if [ ! -f .env ]; then
        echo "Создаем .env файл..."
        cat > .env << 'ENVEOF'
# Telegram Bot Token
BOT_TOKEN=8255931872:AAHzVoCIqd38Kl-4Ru5q9DExTBZkychnIJE

# Yandex GPT API - ЗАМЕНИТЕ НА ВАШИ ДАННЫЕ
YANDEX_GPT_API_KEY=your_yandex_gpt_api_key_here
YANDEX_FOLDER_ID=your_yandex_folder_id_here

# Django
SECRET_KEY=django-insecure-your-secret-key-here
DEBUG=False

# Database
DATABASE_URL=sqlite:///db.sqlite3
ENVEOF
        echo "⚠️  ВАЖНО: Отредактируйте файл .env и укажите ваши API ключи!"
    fi
    
    # Останавливаем существующий бот если он запущен
    echo "🛑 Останавливаем существующий бот..."
    screen -S $SCREEN_NAME -X quit 2>/dev/null || echo "Бот не был запущен"
    
    # Запускаем бота в новом screen
    echo "🤖 Запускаем бота..."
    screen -dmS $SCREEN_NAME bash -c "cd $REMOTE_PATH && source venv/bin/activate && python bot/main.py"
    
    echo "✅ Деплой завершен! Бот запущен в screen '$SCREEN_NAME'"
    echo "Для просмотра логов используйте: screen -r $SCREEN_NAME"
    echo "Для выхода из screen: Ctrl+A, затем D"
EOF

echo "🎉 Деплой успешно завершен!"
echo "Для подключения к screen с ботом выполните:"
echo "ssh $SERVER_USER@$SERVER_HOST"
echo "screen -r $SCREEN_NAME"
