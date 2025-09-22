#!/usr/bin/env python3
"""
Скрипт для инициализации базы данных Django
"""
import os
import sys
import django
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.append(str(Path(__file__).parent))

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'db_app.settings')
django.setup()

from django.core.management import execute_from_command_line

def init_database():
    """Инициализирует базу данных"""
    print("🔄 Инициализация базы данных...")
    
    # Создаем миграции
    print("📝 Создание миграций...")
    execute_from_command_line(['manage.py', 'makemigrations'])
    
    # Применяем миграции
    print("🚀 Применение миграций...")
    execute_from_command_line(['manage.py', 'migrate'])
    
    # Создаем суперпользователя (опционально)
    print("✅ База данных инициализирована!")
    print("\nДля создания суперпользователя выполните:")
    print("python manage.py createsuperuser")

if __name__ == "__main__":
    init_database()


