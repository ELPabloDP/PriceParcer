"""
Конфигурация для PriceParser бота
"""
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Telegram Bot
BOT_TOKEN = os.getenv("BOT_TOKEN", "8255931872:AAHzVoCIqd38Kl-4Ru5q9DExTBZkychnIJE")

# Yandex GPT API
YANDEX_GPT_API_KEY = os.getenv("YANDEX_GPT_API_KEY")
YANDEX_FOLDER_ID = os.getenv("YANDEX_FOLDER_ID")

# Django
SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-your-secret-key-here")
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# Проверяем обязательные переменные
if not YANDEX_GPT_API_KEY:
    print("⚠️  ВНИМАНИЕ: YANDEX_GPT_API_KEY не установлен!")
    print("Создайте файл .env и добавьте:")
    print("YANDEX_GPT_API_KEY=your_api_key_here")
    print("YANDEX_FOLDER_ID=your_folder_id_here")

if not YANDEX_FOLDER_ID:
    print("⚠️  ВНИМАНИЕ: YANDEX_FOLDER_ID не установлен!")
    print("Создайте файл .env и добавьте:")
    print("YANDEX_GPT_API_KEY=your_api_key_here")
    print("YANDEX_FOLDER_ID=your_folder_id_here")


