#!/usr/bin/env python3
"""
Пошаговый тест Apple экосистемы
Тестирует каждую категорию отдельно для детального анализа
"""

import sys
import re
import asyncio
from pathlib import Path
from typing import List, Dict, Any

# Добавляем путь к проекту
sys.path.append(str(Path(__file__).parent))

# Импортируем парсеры
from parsers.iphone_parser import iphone_parser
from parsers.macbook_parser import macbook_parser
from parsers.ipad_parser import iPadParser
from parsers.apple_watch_parser import AppleWatchParser
from parsers.imac_parser import iMacParser
from parsers.airpods_parser import AirPodsParser
from parsers.apple_pencil_parser import ApplePencilParser

# Импортируем гибридный парсер
from services.hybrid_parser import HybridParser

class AppleStepByStepTester:
    """Пошаговый тестер Apple устройств"""
    
    def __init__(self):
        self.examples_file = Path(__file__).parent / "bot" / "exampleprices.txt"
        self.hybrid_parser = HybridParser()
    
    def extract_lines_from_file(self) -> List[str]:
        """Извлекает все строки из файла примеров"""
        if not self.examples_file.exists():
            print(f"❌ Файл примеров не найден: {self.examples_file}")
            return []
        
        with open(self.examples_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Фильтруем строки
        filtered_lines = []
        for line in lines:
            line = line.strip()
            if not line or line.startswith('Top Re:sale') or '🍎' in line or line.startswith('—'):
                continue
            if any(char in line for char in ['🔥', '💻💻', '⚫️', '➖', '🔴', '🟥', '🔗', '🚗', '🏎️']):
                continue
            filtered_lines.append(line)
        
        return filtered_lines
    
    def extract_iphone_lines(self, lines: List[str]) -> List[str]:
        """Извлекает строки с iPhone"""
        iphone_patterns = [
            r'\b\d{1,2}[A-Z]?\s+(Pro\s+Max|Pro\s+Maх|Pro|Plus)?\s*\d+\s*(GB|TB)?\s+[A-Za-z\s]+.*\d+.*[🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳🇦🇺🇸🇬🇮🇪🇲🇴🇰🇷🇬🇹🇹🇭🇵🇾🇨🇱]',
            r'iPhone\s+\d{1,2}[A-Z]?\s+(Pro\s+Max|Pro|Plus)?\s*\d+.*[🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳🇦🇺🇸🇬🇮🇪🇲🇴🇰🇷🇬🇹🇹🇭🇵🇾🇨🇱]',
            r'Apple iPhone \d+.*\d+.*[🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳🇦🇺🇸🇬🇮🇪🇲🇴🇰🇷🇬🇹🇹🇭🇵🇾🇨🇱]'
        ]
        
        iphone_lines = []
        for line in lines:
            for pattern in iphone_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    iphone_lines.append(line)
                    break
        
        return iphone_lines
    
    def extract_ipad_lines(self, lines: List[str]) -> List[str]:
        """Извлекает строки с iPad"""
        ipad_patterns = [
            r'iPad.*\d+.*[🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]',
            r'MINI.*\d+.*[🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]',
            r'AIR.*\d+.*[🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]',
            r'Apple iPad.*\d+.*[🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]'
        ]
        
        ipad_lines = []
        for line in lines:
            for pattern in ipad_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    ipad_lines.append(line)
                    break
        
        return ipad_lines
    
    def extract_macbook_lines(self, lines: List[str]) -> List[str]:
        """Извлекает строки с MacBook"""
        macbook_patterns = [
            r'MacBook.*[🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]',
            r'💻.*MacBook.*\d+',
            r'Mac Mini.*\d+',
            r'💻.*Air.*\d+',
            r'💻.*Pro.*\d+',
            r'Apple MacBook.*\d+'
        ]
        
        macbook_lines = []
        for line in lines:
            for pattern in macbook_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    macbook_lines.append(line)
                    break
        
        return macbook_lines
    
    async def test_iphone_parsing(self):
        """Тестирует парсинг iPhone"""
        print("🍎📱 ТЕСТИРОВАНИЕ iPhone ПАРСИНГА")
        print("=" * 50)
        
        # Извлекаем строки
        all_lines = self.extract_lines_from_file()
        iphone_lines = self.extract_iphone_lines(all_lines)
        
        print(f"📊 Найдено iPhone строк: {len(iphone_lines)}")
        
        if not iphone_lines:
            print("❌ Не найдено iPhone строк для тестирования!")
            return
        
        # Показываем первые 10 строк для проверки
        print("\n🔍 Примеры найденных iPhone строк:")
        for i, line in enumerate(iphone_lines[:10], 1):
            print(f"  {i:2}. {line}")
        
        if len(iphone_lines) > 10:
            print(f"  ... и еще {len(iphone_lines) - 10} строк")
        
        # Тестируем индивидуальный парсер
        print(f"\n🧪 Тестируем iPhone парсер:")
        parsed_count = 0
        failed_lines = []
        
        for line in iphone_lines:
            try:
                result = iphone_parser.parse_line(line)
                if result:
                    parsed_count += 1
                else:
                    failed_lines.append(line)
            except Exception as e:
                failed_lines.append(f"{line} (ERROR: {e})")
        
        success_rate = (parsed_count / len(iphone_lines)) * 100
        print(f"  ✅ Распознано: {parsed_count}/{len(iphone_lines)} ({success_rate:.1f}%)")
        
        if failed_lines:
            print(f"\n❌ Нераспознанные строки ({len(failed_lines)}):")
            for line in failed_lines[:5]:  # Показываем только первые 5
                print(f"    {line}")
            if len(failed_lines) > 5:
                print(f"    ... и еще {len(failed_lines) - 5}")
        
        # Тестируем гибридный парсер
        print(f"\n🔄 Тестируем через гибридный парсер:")
        test_message = "\n".join(iphone_lines)
        
        try:
            result = await self.hybrid_parser.parse_message(test_message, "test_iphone")
            
            total_saved = result.get('total_saved', 0)
            template_saved = result.get('template_saved', 0) 
            gpt_saved = result.get('gpt_saved', 0)
            
            print(f"  📊 Всего сохранено: {total_saved}")
            print(f"  🎯 Шаблонами: {template_saved}")
            print(f"  🤖 GPT: {gpt_saved}")
            
            hybrid_success = (total_saved / len(iphone_lines)) * 100
            print(f"  📈 Успешность: {hybrid_success:.1f}%")
            
            if gpt_saved > 0:
                print(f"  ⚠️  {gpt_saved} строк обработано через GPT - нужно улучшить шаблоны!")
            else:
                print(f"  🎉 Все iPhone распознаются шаблонами!")
                
        except Exception as e:
            print(f"  💥 Ошибка гибридного парсера: {e}")
    
    async def test_ipad_parsing(self):
        """Тестирует парсинг iPad"""
        print("\n🍎📱 ТЕСТИРОВАНИЕ iPad ПАРСИНГА")
        print("=" * 50)
        
        # Извлекаем строки
        all_lines = self.extract_lines_from_file()
        ipad_lines = self.extract_ipad_lines(all_lines)
        
        print(f"📊 Найдено iPad строк: {len(ipad_lines)}")
        
        if not ipad_lines:
            print("❌ Не найдено iPad строк для тестирования!")
            return
        
        # Показываем первые 10 строк для проверки
        print("\n🔍 Примеры найденных iPad строк:")
        for i, line in enumerate(ipad_lines[:10], 1):
            print(f"  {i:2}. {line}")
        
        if len(ipad_lines) > 10:
            print(f"  ... и еще {len(ipad_lines) - 10} строк")
        
        # Тестируем индивидуальный парсер
        print(f"\n🧪 Тестируем iPad парсер:")
        parsed_count = 0
        failed_lines = []
        
        for line in ipad_lines:
            try:
                result = ipad_parser.parse_line(line)
                if result:
                    parsed_count += 1
                else:
                    failed_lines.append(line)
            except Exception as e:
                failed_lines.append(f"{line} (ERROR: {e})")
        
        success_rate = (parsed_count / len(ipad_lines)) * 100
        print(f"  ✅ Распознано: {parsed_count}/{len(ipad_lines)} ({success_rate:.1f}%)")
        
        if failed_lines:
            print(f"\n❌ Нераспознанные строки ({len(failed_lines)}):")
            for line in failed_lines[:10]:  # Показываем первые 10
                print(f"    {line}")
            if len(failed_lines) > 10:
                print(f"    ... и еще {len(failed_lines) - 10}")
        
        # Тестируем гибридный парсер
        print(f"\n🔄 Тестируем через гибридный парсер:")
        test_message = "\n".join(ipad_lines)
        
        try:
            result = await self.hybrid_parser.parse_message(test_message, "test_ipad")
            
            total_saved = result.get('total_saved', 0)
            template_saved = result.get('template_saved', 0)
            gpt_saved = result.get('gpt_saved', 0)
            
            print(f"  📊 Всего сохранено: {total_saved}")
            print(f"  🎯 Шаблонами: {template_saved}")
            print(f"  🤖 GPT: {gpt_saved}")
            
            hybrid_success = (total_saved / len(ipad_lines)) * 100
            print(f"  📈 Успешность: {hybrid_success:.1f}%")
            
            if gpt_saved > 0:
                print(f"  ⚠️  {gpt_saved} строк обработано через GPT - нужно улучшить шаблоны!")
            else:
                print(f"  🎉 Все iPad распознаются шаблонами!")
                
        except Exception as e:
            print(f"  💥 Ошибка гибридного парсера: {e}")
    
    async def test_macbook_parsing(self):
        """Тестирует парсинг MacBook"""
        print("\n🍎💻 ТЕСТИРОВАНИЕ MacBook ПАРСИНГА")
        print("=" * 50)
        
        # Извлекаем строки
        all_lines = self.extract_lines_from_file()
        macbook_lines = self.extract_macbook_lines(all_lines)
        
        print(f"📊 Найдено MacBook строк: {len(macbook_lines)}")
        
        if not macbook_lines:
            print("❌ Не найдено MacBook строк для тестирования!")
            return
        
        # Показываем первые 10 строк для проверки
        print("\n🔍 Примеры найденных MacBook строк:")
        for i, line in enumerate(macbook_lines[:10], 1):
            print(f"  {i:2}. {line}")
        
        if len(macbook_lines) > 10:
            print(f"  ... и еще {len(macbook_lines) - 10} строк")
        
        # Тестируем индивидуальный парсер
        print(f"\n🧪 Тестируем MacBook парсер:")
        parsed_count = 0
        failed_lines = []
        
        for line in macbook_lines:
            try:
                result = macbook_parser.parse_line(line)
                if result:
                    parsed_count += 1
                else:
                    failed_lines.append(line)
            except Exception as e:
                failed_lines.append(f"{line} (ERROR: {e})")
        
        success_rate = (parsed_count / len(macbook_lines)) * 100
        print(f"  ✅ Распознано: {parsed_count}/{len(macbook_lines)} ({success_rate:.1f}%)")
        
        if failed_lines:
            print(f"\n❌ Нераспознанные строки ({len(failed_lines)}):")
            for line in failed_lines[:10]:  # Показываем первые 10
                print(f"    {line}")
            if len(failed_lines) > 10:
                print(f"    ... и еще {len(failed_lines) - 10}")
        
        # Тестируем гибридный парсер
        print(f"\n🔄 Тестируем через гибридный парсер:")
        test_message = "\n".join(macbook_lines)
        
        try:
            result = await self.hybrid_parser.parse_message(test_message, "test_macbook")
            
            total_saved = result.get('total_saved', 0)
            template_saved = result.get('template_saved', 0)
            gpt_saved = result.get('gpt_saved', 0)
            
            print(f"  📊 Всего сохранено: {total_saved}")
            print(f"  🎯 Шаблонами: {template_saved}")
            print(f"  🤖 GPT: {gpt_saved}")
            
            hybrid_success = (total_saved / len(macbook_lines)) * 100
            print(f"  📈 Успешность: {hybrid_success:.1f}%")
            
            if gpt_saved > 0:
                print(f"  ⚠️  {gpt_saved} строк обработано через GPT - нужно улучшить шаблоны!")
            else:
                print(f"  🎉 Все MacBook распознаются шаблонами!")
                
        except Exception as e:
            print(f"  💥 Ошибка гибридного парсера: {e}")

async def main():
    """Главная функция"""
    tester = AppleStepByStepTester()
    
    print("Выберите, что тестировать:")
    print("1. iPhone")
    print("2. iPad") 
    print("3. MacBook")
    print("4. Все по очереди")
    
    choice = input("\nВведите номер (1-4): ").strip()
    
    if choice == "1":
        await tester.test_iphone_parsing()
    elif choice == "2":
        await tester.test_ipad_parsing()
    elif choice == "3":
        await tester.test_macbook_parsing()
    elif choice == "4":
        await tester.test_iphone_parsing()
        await tester.test_ipad_parsing()
        await tester.test_macbook_parsing()
    else:
        print("❌ Неверный выбор!")

if __name__ == "__main__":
    asyncio.run(main())
