# Price Parser Bot

Telegram бот для парсинга цен на продукты Apple (iPhone, iPad, MacBook, Apple Watch).

## 🚀 Быстрый старт

### Локальная разработка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/ELPabloDP/PriceParcer.git
cd PriceParcer
```

2. Создайте виртуальное окружение:
```bash
python3 -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Настройте конфигурацию в `config.py`

5. Запустите бота:
```bash
python bot/main.py
```

### Деплой на сервер

#### Автоматический деплой (рекомендуется)

1. Настройте GitHub Secrets в настройках репозитория:
   - `SERVER_HOST`: IP адрес сервера (147.45.143.18)
   - `SERVER_USER`: имя пользователя (root)
   - `SERVER_PASSWORD`: пароль сервера

2. Просто делайте push в main ветку - деплой произойдет автоматически!

#### Ручной деплой

Используйте готовые скрипты:

```bash
# Полный деплой (коммит + пуш + деплой на сервер)
./deploy.sh

# Только перезапуск бота на сервере
./restart_bot.sh

# Просмотр логов бота
./logs.sh
```

## 📁 Структура проекта

```
PriceParcer/
├── bot/                    # Telegram бот
│   ├── main.py            # Главный файл бота
│   ├── handlers.py        # Обработчики команд
│   └── ...
├── parsers/               # Парсеры для разных продуктов
│   ├── iphone_parser.py
│   ├── ipad_parser.py
│   └── ...
├── services/              # Сервисы для работы с данными
├── db_app/                # Django приложение для БД
├── deploy.sh              # Скрипт деплоя
├── restart_bot.sh         # Скрипт перезапуска
└── logs.sh               # Скрипт просмотра логов
```

## 🔧 Управление ботом на сервере

### Подключение к серверу
```bash
ssh root@147.45.143.18
```

### Работа с screen
```bash
# Просмотр всех screen сессий
screen -ls

# Подключение к боту
screen -r price_parser_bot

# Выход из screen (не останавливая процесс)
Ctrl+A, затем D

# Остановка бота
screen -S price_parser_bot -X quit
```

### Просмотр логов
```bash
# Через скрипт (с локальной машины)
./logs.sh

# Или напрямую на сервере
screen -r price_parser_bot
```

## 🛠 CI/CD

Проект настроен с автоматическим CI/CD через GitHub Actions:

- При каждом push в main ветку происходит автоматический деплой
- Бот автоматически перезапускается с новым кодом
- Можно запустить деплой вручную через GitHub Actions

## 📝 Полезные команды

```bash
# Проверка статуса бота на сервере
ssh root@147.45.143.18 "screen -ls"

# Перезапуск бота
ssh root@147.45.143.18 "screen -S price_parser_bot -X quit && screen -dmS price_parser_bot bash -c 'cd /root/PriceParcer && source venv/bin/activate && python bot/main.py'"

# Просмотр использования ресурсов
ssh root@147.45.143.18 "htop"
```

## 🔐 Безопасность

- Пароли и токены хранятся в GitHub Secrets
- SSH ключи настроены для безопасного подключения
- Виртуальное окружение изолирует зависимости
