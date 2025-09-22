#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для инициализации базы данных
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'db_settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == '__main__':
    # Инициализация Django
    django.setup()
    
    # Создание миграций
    print("🔄 Создание миграций...")
    execute_from_command_line(['manage.py', 'makemigrations'])
    
    # Применение миграций
    print("🔄 Применение миграций...")
    execute_from_command_line(['manage.py', 'migrate'])
    
    print("✅ База данных инициализирована!")

