#!/bin/bash

# Быстрый деплой с коммитом изменений
# Использование: ./quick_deploy.sh "Описание изменений"

set -e

# Получаем описание изменений из аргумента или используем стандартное
COMMIT_MESSAGE="${1:-Update: $(date '+%Y-%m-%d %H:%M:%S')}"

echo "🚀 Быстрый деплой проекта PriceParcer"
echo "📝 Сообщение коммита: $COMMIT_MESSAGE"
echo "=" * 50

# Проверяем статус git
echo "📊 Проверяем статус Git..."
git status --porcelain

# Добавляем все изменения
echo "📝 Добавляем изменения в Git..."
git add .

# Коммитим изменения
echo "💾 Коммитим изменения..."
git commit -m "$COMMIT_MESSAGE"

# Пушим в GitHub
echo "⬆️ Пушим в GitHub..."
git push origin main

echo "✅ Изменения успешно запушены в GitHub!"
echo "🔄 Теперь запускаем деплой на сервер..."

# Запускаем основной скрипт деплоя
./deploy.sh

echo "🎉 Быстрый деплой завершен!"
