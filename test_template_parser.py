#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы парсера только на шаблонах
"""
import asyncio
import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.append(str(Path(__file__).parent))

from services.hybrid_parser import template_parser

async def test_parser():
    """Тестирует парсер на различных типах прайсов"""
    
    # Тестовые данные
    test_cases = [
        {
            "name": "iPhone прайсы",
            "text": """🇺🇸16 128 White - 58900
13 128 Midnight - 38000🇮🇳
15Pro 128 Blue - 78500🇦🇪
16 Plus 128 Teal 🇮🇳 60200"""
        },
        {
            "name": "MacBook прайсы",
            "text": """🇺🇸 MGND3 - 8/256 Gold — 62.000₽
MW0Y3 13" M4 10/8 16 256GB Starlight - 80.000
MacBook Air 13 M3: 8/256GB Gray - 69000"""
        },
        {
            "name": "Смешанные прайсы",
            "text": """iPhone 13 128GB Black 🇺🇸 35000
MacBook Air 13 M2 8/256GB Silver 65000🇯🇵
iPad Pro 11 M4 256GB Space Black 85000🇰🇷
Не распознаваемая строка без цены
Гарантия 1 год - не товар"""
        },
        {
            "name": "Только нераспознаваемые строки",
            "text": """Просто текст без прайсов
Еще одна строка
И еще одна"""
        }
    ]
    
    print("🧪 Тестирование парсера только на шаблонах\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"📋 Тест {i}: {test_case['name']}")
        print(f"Входные данные:\n{test_case['text']}\n")
        
        try:
            results = await template_parser.parse_message(test_case['text'], "Тест")
            
            print("Результат:")
            print(results['summary'])
            print("\n" + "="*50 + "\n")
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    asyncio.run(test_parser())
