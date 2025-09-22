# 🚀 Инструкция по деплою и управлению ботом

## 📋 Быстрый старт

### 1. Первоначальная настройка сервера

```bash
# Запустите полный деплой
./deploy.sh
```

### 2. Настройка API ключей

```bash
# Отредактируйте .env файл на сервере
./edit_env.sh
```

В файле .env укажите ваши реальные API ключи:
- `YANDEX_GPT_API_KEY` - ваш ключ от Yandex GPT
- `YANDEX_FOLDER_ID` - ID папки в Yandex Cloud

### 3. Запуск бота

```bash
# Перезапустите бота с новыми настройками
./restart_bot.sh
```

## 🛠 Управление ботом

### Основные команды

```bash
# Полный деплой (коммит + пуш + деплой)
./deploy.sh

# Только перезапуск бота
./restart_bot.sh

# Просмотр логов
./logs.sh

# Редактирование настроек
./edit_env.sh
```

### Прямое подключение к серверу

```bash
# Подключение к серверу
ssh root@147.45.143.18

# Просмотр всех screen сессий
screen -ls

# Подключение к боту
screen -r price_parser_bot

# Выход из screen (не останавливая бота)
Ctrl+A, затем D

# Остановка бота
screen -S price_parser_bot -X quit
```

## 🔄 CI/CD процесс

### Автоматический деплой

1. **Настройте GitHub Secrets** в настройках репозитория:
   - `SERVER_HOST`: 147.45.143.18
   - `SERVER_USER`: root
   - `SERVER_PASSWORD`: fh3su31XNgJ^1N

2. **Любой push в main ветку** автоматически:
   - Обновляет код на сервере
   - Перезапускает бота
   - Применяет все изменения

### Ручной деплой через GitHub Actions

1. Перейдите в раздел "Actions" на GitHub
2. Выберите workflow "Deploy to Server"
3. Нажмите "Run workflow"

## 📊 Мониторинг

### Проверка статуса

```bash
# Проверка screen сессий
ssh root@147.45.143.18 "screen -ls"

# Проверка процессов Python
ssh root@147.45.143.18 "ps aux | grep python"

# Использование ресурсов
ssh root@147.45.143.18 "htop"
```

### Просмотр логов

```bash
# Через скрипт
./logs.sh

# Или напрямую
ssh root@147.45.143.18 "screen -r price_parser_bot"
```

## 🔧 Устранение неполадок

### Бот не запускается

1. Проверьте .env файл:
```bash
./edit_env.sh
```

2. Проверьте логи:
```bash
./logs.sh
```

3. Перезапустите бота:
```bash
./restart_bot.sh
```

### Ошибки API

1. Убедитесь, что API ключи корректны
2. Проверьте лимиты API
3. Проверьте интернет соединение на сервере

### Проблемы с Git

1. Проверьте статус:
```bash
git status
```

2. Принудительно обновите сервер:
```bash
ssh root@147.45.143.18 "cd /root/PriceParcer && git pull origin main"
```

## 📝 Полезные команды

```bash
# Обновление только кода (без перезапуска)
ssh root@147.45.143.18 "cd /root/PriceParcer && git pull origin main"

# Установка новых зависимостей
ssh root@147.45.143.18 "cd /root/PriceParcer && source venv/bin/activate && pip install -r requirements.txt"

# Очистка логов
ssh root@147.45.143.18 "cd /root/PriceParcer && find . -name '*.log' -delete"

# Резервное копирование базы данных
ssh root@147.45.143.18 "cd /root/PriceParcer && cp db.sqlite3 db_backup_$(date +%Y%m%d_%H%M%S).sqlite3"
```

## 🎯 Workflow для разработки

1. **Внесите изменения** в код локально
2. **Протестируйте** локально
3. **Закоммитьте** изменения:
   ```bash
   git add .
   git commit -m "Описание изменений"
   git push origin main
   ```
4. **Автоматический деплой** произойдет через GitHub Actions
5. **Проверьте** работу бота через `./logs.sh`

## 🔐 Безопасность

- Все пароли и ключи хранятся в GitHub Secrets
- .env файл не попадает в Git репозиторий
- SSH подключение защищено паролем
- Виртуальное окружение изолирует зависимости

---

**Готово!** 🎉 Ваш бот настроен с полным CI/CD процессом!
