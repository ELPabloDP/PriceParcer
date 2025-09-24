#!/usr/bin/env python3
"""
Тестирование iPhone парсера
Извлекает все iPhone строки и тестирует их через парсер
"""

import sys
import re
from pathlib import Path
from typing import List

# Добавляем путь к проекту
sys.path.append(str(Path(__file__).parent))

# Импортируем парсер
from parsers.iphone_parser import iphone_parser

class iPhoneParserTester:
    """Тестер iPhone парсера"""
    
    def __init__(self):
        self.examples_file = Path(__file__).parent / "bot" / "exampleprices.txt"
    
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
    
    def test_iphone_parser(self):
        """Тестирует iPhone парсер"""
        print("🍎📱 ТЕСТИРОВАНИЕ iPhone ПАРСЕРА")
        print("=" * 50)
        
        # Извлекаем строки
        all_lines = self.extract_lines_from_file()
        iphone_lines = self.extract_iphone_lines(all_lines)
        
        print(f"📊 Найдено iPhone строк: {len(iphone_lines)}")
        
        if not iphone_lines:
            print("❌ Не найдено iPhone строк для тестирования!")
            return
        
        # Показываем все строки для анализа
        print("\n🔍 Все найденные iPhone строки:")
        for i, line in enumerate(iphone_lines, 1):
            print(f"  {i:2}. {line}")
        
        # Тестируем парсер
        print(f"\n🧪 Тестируем iPhone парсер:")
        parsed_count = 0
        failed_lines = []
        
        for i, line in enumerate(iphone_lines, 1):
            try:
                # iPhone парсер использует parse_lines, а не parse_line
                parsed_items, unparsed = iphone_parser.parse_lines([line])
                if parsed_items:
                    parsed_count += 1
                    print(f"  ✅ {i:2}. {line}")
                    for item in parsed_items:
                        print(f"      Результат: {item}")
                else:
                    failed_lines.append(line)
                    print(f"  ❌ {i:2}. {line}")
            except Exception as e:
                failed_lines.append(f"{line} (ERROR: {e})")
                print(f"  💥 {i:2}. {line} (ERROR: {e})")
        
        success_rate = (parsed_count / len(iphone_lines)) * 100
        print(f"\n📊 РЕЗУЛЬТАТЫ:")
        print(f"  ✅ Распознано: {parsed_count}/{len(iphone_lines)} ({success_rate:.1f}%)")
        print(f"  ❌ Нераспознано: {len(failed_lines)}")
        
        if failed_lines:
            print(f"\n❌ НЕРАСПОЗНАННЫЕ СТРОКИ ({len(failed_lines)}):")
            for i, line in enumerate(failed_lines, 1):
                print(f"  {i:2}. {line}")
        
        return failed_lines

def main():
    """Главная функция"""
    tester = iPhoneParserTester()
    failed_lines = tester.test_iphone_parser()
    
    if failed_lines:
        print(f"\n🔧 НУЖНО ДОБАВИТЬ ПАТТЕРНЫ ДЛЯ {len(failed_lines)} СТРОК")
        print("Проанализируйте нераспознанные строки и добавьте соответствующие regex паттерны в iphone_parser.py")

if __name__ == "__main__":
    main()
