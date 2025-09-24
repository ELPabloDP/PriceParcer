#!/usr/bin/env python3
"""
Тестовый скрипт для проверки новых шаблонов iPhone парсера
"""
import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.append(str(Path(__file__).parent))

from parsers.iphone_parser import iphone_parser

def test_iphone_patterns():
    """Тестирует новые шаблоны iPhone парсера"""
    
    # Проблемные строки из сообщения пользователя
    test_lines = [
        "16 128 Black 58800 🇨🇳2Sim",
        "16 Prо 128 White 88100🇯🇵",
        "16 Prо 128 White 79300🇨🇳2Sim",
        "16 Prо 128 Desert 81500🇨🇳2Sim",
        "16 Prо 128 Desert 75700🇺🇸",
        "16 Prо 256 White 96300🇨🇳2Sim",
        "16 Prо Maх 512 White 115600🇯🇵",
        "16 Prо Maх 1TB Black 136000🇯🇵",
        "16 Pro 128 Black 87300🇯🇵",
        "16 Pro 128 Black 80100🇨🇳2Sim",
        "16 Pro Max 256 Black 10100🇨🇳2Sim",  # Проблема с ценой 10100 вместо 101200
        "16 Pro Max 256 Natural 10500🇨🇳2Sim",  # Проблема с ценой 10500 вместо 105000
    ]
    
    print("🧪 Тестирование новых шаблонов iPhone парсера\n")
    
    for i, line in enumerate(test_lines, 1):
        print(f"📱 Тест {i}: {line}")
        
        # Проверяем, распознается ли строка как iPhone
        is_iphone = iphone_parser._is_iphone_line(line)
        print(f"   Распознано как iPhone: {is_iphone}")
        
        if is_iphone:
            # Парсим строку
            parsed_data, unparsed_lines = iphone_parser.parse_lines([line])
            
            if parsed_data:
                data = parsed_data[0]
                print(f"   ✅ Распарсено:")
                print(f"      Поколение: {data.generation}")
                print(f"      Вариант: '{data.variant}'")
                print(f"      Память: {data.storage}")
                print(f"      Цвет: {data.color}")
                print(f"      Страна: {data.country_flag}")
                print(f"      SIM: {data.country_code}")
                print(f"      Цена: {data.price}")
            else:
                print(f"   ❌ Не распарсено")
                print(f"   Нераспознанные: {unparsed_lines}")
        else:
            print(f"   ❌ Не распознано как iPhone")
        
        print()

if __name__ == "__main__":
    test_iphone_patterns()
