#!/usr/bin/env python3
"""
Комплексный тест Apple экосистемы
Извлекает все Apple прайсы из файла примеров и тестирует парсинг
"""

import sys
import re
import asyncio
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple

# Добавляем путь к проекту
sys.path.append(str(Path(__file__).parent))

# Импортируем парсеры
from parsers.iphone_parser import iphone_parser
from parsers.macbook_parser import macbook_parser
from parsers.ipad_parser import ipad_parser
from parsers.apple_watch_parser import AppleWatchParser
from parsers.imac_parser import iMacParser
from parsers.airpods_parser import AirPodsParser
from parsers.apple_pencil_parser import ApplePencilParser

# Импортируем гибридный парсер
from services.hybrid_parser import HybridParser

class AppleEcosystemTester:
    """Тестер всей экосистемы Apple"""
    
    def __init__(self):
        self.examples_file = Path(__file__).parent / "bot" / "exampleprices.txt"
        
        # Инициализируем парсеры
        self.parsers = {
            'iPhone': iphone_parser,
            'MacBook': macbook_parser,
            'iPad': ipad_parser,
            'Apple Watch': AppleWatchParser(),
            'iMac': iMacParser(),
            'AirPods': AirPodsParser(),
            'Apple Pencil': ApplePencilParser()
        }
        
        self.hybrid_parser = HybridParser()
        
        # Категории для сортировки
        self.categories = {
            'iPhone': [],
            'MacBook': [],
            'iPad': [],
            'Apple Watch': [],
            'iMac': [],
            'AirPods': [],
            'Apple Pencil': []
        }
    
    def extract_apple_prices(self) -> Dict[str, List[str]]:
        """Извлекает все Apple прайсы из файла примеров"""
        if not self.examples_file.exists():
            print(f"❌ Файл примеров не найден: {self.examples_file}")
            return {}
        
        print(f"📂 Читаем файл: {self.examples_file}")
        
        with open(self.examples_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Паттерны для каждой категории
        patterns = {
            'iPhone': [
                r'\b(iPhone\s+)?\d{1,2}[A-Z]?\s+(Pro\s+Max|Pro|Plus)?\s*\d+\s*(GB|TB)?\s+[A-Za-z\s]+.*\d+.*[🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳🇦🇺🇸🇬🇮🇪🇲🇴🇰🇷🇬🇹🇹🇭🇵🇾🇨🇱]',
                r'\b\d{1,2}[A-Z]?\s+(Pro\s+Max|Pro|Plus)?\s*\d+.*[🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳🇦🇺🇸🇬🇮🇪🇲🇴🇰🇷🇬🇹🇹🇭🇵🇾🇨🇱]',
                r'Apple iPhone \d+.*\d+.*[🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳🇦🇺🇸🇬🇮🇪🇲🇴🇰🇷🇬🇹🇹🇭🇵🇾🇨🇱]'
            ],
            'MacBook': [
                r'MacBook.*[🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]',
                r'💻.*MacBook.*\d+',
                r'Mac Mini.*\d+',
                r'💻.*Air.*\d+',
                r'💻.*Pro.*\d+'
            ],
            'iPad': [
                r'iPad.*[🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]',
                r'MINI.*\d+.*[🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]',
                r'AIR.*\d+.*[🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]'
            ],
            'Apple Watch': [
                r'Apple Watch.*\d+',
                r'SE.*\d+.*mm.*\d+',
                r'Ultra.*\d+.*mm.*\d+',
                r'S\d+.*\d+.*mm.*\d+',
                r'AW.*\d+.*mm.*\d+',
                r'Watch.*\d+.*mm.*\d+'
            ],
            'iMac': [
                r'iMac.*[🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]',
                r'Mac Mini.*\d+',
                r'💻.*Mini.*\d+'
            ],
            'AirPods': [
                r'AirPods.*\d+',
                r'🎧.*AirPods.*\d+',
                r'🎧.*\d+.*[🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]'
            ],
            'Apple Pencil': [
                r'Apple Pencil.*\d+',
                r'Pencil.*\d+',
                r'✒️.*Pencil.*\d+'
            ]
        }
        
        print("🔍 Извлекаем Apple прайсы по категориям...")
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('Top Re:sale') or '🍎' in line:
                continue
            
            # Проверяем каждую категорию
            for category, category_patterns in patterns.items():
                for pattern in category_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        self.categories[category].append(line)
                        break
        
        # Выводим статистику
        print("\n📊 Статистика извлеченных прайсов:")
        total = 0
        for category, items in self.categories.items():
            count = len(items)
            total += count
            print(f"  {category}: {count} строк")
        
        print(f"\n🎯 Всего Apple прайсов найдено: {total}")
        return self.categories
    
    def test_individual_parsers(self) -> Dict[str, Tuple[int, int]]:
        """Тестирует каждый парсер индивидуально"""
        print("\n🧪 ТЕСТИРОВАНИЕ ИНДИВИДУАЛЬНЫХ ПАРСЕРОВ")
        print("=" * 60)
        
        results = {}
        
        for category, lines in self.categories.items():
            if not lines:
                continue
            
            print(f"\n📱 Тестируем {category} парсер:")
            print(f"   Строк для тестирования: {len(lines)}")
            
            parser = self.parsers[category]
            
            try:
                if hasattr(parser, 'parse_lines'):
                    # Новые парсеры
                    parsed_items, unparsed_lines = parser.parse_lines(lines)
                    parsed_count = len(parsed_items)
                    unparsed_count = len(unparsed_lines)
                else:
                    # Старые парсеры (iPhone, MacBook, iPad)
                    parsed_count = 0
                    unparsed_count = 0
                    for line in lines:
                        try:
                            result = parser.parse_line(line)
                            if result:
                                parsed_count += 1
                            else:
                                unparsed_count += 1
                        except:
                            unparsed_count += 1
                
                success_rate = (parsed_count / len(lines)) * 100 if lines else 0
                
                print(f"   ✅ Распознано: {parsed_count}")
                print(f"   ❌ Не распознано: {unparsed_count}")
                print(f"   📊 Точность: {success_rate:.1f}%")
                
                if unparsed_count > 0 and unparsed_count <= 5:
                    print(f"   🔍 Нераспознанные строки:")
                    if hasattr(parser, 'parse_lines'):
                        for line in unparsed_lines[:5]:
                            print(f"      ❌ {line}")
                    
                results[category] = (parsed_count, unparsed_count)
                
            except Exception as e:
                print(f"   💥 Ошибка тестирования: {e}")
                results[category] = (0, len(lines))
        
        return results
    
    async def test_hybrid_parser(self) -> Dict[str, int]:
        """Тестирует гибридный парсер"""
        print("\n🔄 ТЕСТИРОВАНИЕ ГИБРИДНОГО ПАРСЕРА")
        print("=" * 60)
        
        results = {}
        
        for category, lines in self.categories.items():
            if not lines:
                continue
            
            print(f"\n📱 Тестируем {category} через гибридный парсер:")
            
            # Объединяем строки в одно сообщение
            test_message = "\n".join(lines)
            
            try:
                result = await self.hybrid_parser.parse_message(test_message, f"test_{category.lower().replace(' ', '_')}")
                
                total_saved = result.get('total_saved', 0)
                template_saved = result.get('template_saved', 0)
                gpt_saved = result.get('gpt_saved', 0)
                
                print(f"   📊 Всего сохранено: {total_saved}")
                print(f"   🎯 Шаблонами: {template_saved}")
                print(f"   🤖 GPT: {gpt_saved}")
                
                success_rate = (total_saved / len(lines)) * 100 if lines else 0
                print(f"   📈 Успешность: {success_rate:.1f}%")
                
                results[category] = {
                    'total': len(lines),
                    'saved': total_saved,
                    'template': template_saved,
                    'gpt': gpt_saved,
                    'success_rate': success_rate
                }
                
            except Exception as e:
                print(f"   💥 Ошибка: {e}")
                results[category] = {
                    'total': len(lines),
                    'saved': 0,
                    'template': 0,
                    'gpt': 0,
                    'success_rate': 0
                }
        
        return results
    
    def generate_report(self, parser_results: Dict[str, Tuple[int, int]], hybrid_results: Dict[str, Dict]) -> None:
        """Генерирует итоговый отчет"""
        print("\n📋 ИТОГОВЫЙ ОТЧЕТ")
        print("=" * 60)
        
        total_lines = sum(len(lines) for lines in self.categories.values())
        total_parsed_individual = sum(parsed for parsed, _ in parser_results.values())
        total_saved_hybrid = sum(result['saved'] for result in hybrid_results.values())
        
        print(f"\n🎯 ОБЩАЯ СТАТИСТИКА:")
        print(f"   Всего Apple прайсов: {total_lines}")
        print(f"   Распознано индивидуальными парсерами: {total_parsed_individual}")
        print(f"   Сохранено гибридным парсером: {total_saved_hybrid}")
        
        overall_individual = (total_parsed_individual / total_lines) * 100 if total_lines else 0
        overall_hybrid = (total_saved_hybrid / total_lines) * 100 if total_lines else 0
        
        print(f"   Точность индивидуальных парсеров: {overall_individual:.1f}%")
        print(f"   Точность гибридного парсера: {overall_hybrid:.1f}%")
        
        print(f"\n📊 ДЕТАЛИЗАЦИЯ ПО КАТЕГОРИЯМ:")
        for category in self.categories.keys():
            if category not in parser_results:
                continue
                
            lines_count = len(self.categories[category])
            parsed_individual, unparsed_individual = parser_results[category]
            hybrid_data = hybrid_results.get(category, {})
            
            print(f"\n   {category}:")
            print(f"     Строк: {lines_count}")
            print(f"     Индивидуальный парсер: {parsed_individual}/{lines_count} ({(parsed_individual/lines_count)*100:.1f}%)")
            if hybrid_data:
                template_count = hybrid_data['template']
                gpt_count = hybrid_data['gpt']
                total_hybrid = hybrid_data['saved']
                print(f"     Гибридный парсер: {total_hybrid}/{lines_count} ({hybrid_data['success_rate']:.1f}%)")
                print(f"       └── Шаблонами: {template_count}")
                print(f"       └── GPT: {gpt_count}")
        
        # Проверяем цель "все на шаблонах"
        total_template = sum(result['template'] for result in hybrid_results.values())
        total_gpt = sum(result['gpt'] for result in hybrid_results.values())
        
        print(f"\n🎯 ЦЕЛЬ 'ВСЕ НА ШАБЛОНАХ':")
        print(f"   Шаблонами: {total_template}")
        print(f"   GPT: {total_gpt}")
        
        if total_gpt == 0:
            print("   🎉 ЦЕЛЬ ДОСТИГНУТА! Все товары распознаются шаблонами!")
        else:
            print(f"   ⚠️  Еще {total_gpt} товаров обрабатывается через GPT")
    
    async def run_full_test(self):
        """Запускает полный тест экосистемы"""
        print("🍎 КОМПЛЕКСНОЕ ТЕСТИРОВАНИЕ APPLE ЭКОСИСТЕМЫ")
        print("=" * 60)
        
        # Извлекаем прайсы
        categories = self.extract_apple_prices()
        
        if not any(categories.values()):
            print("❌ Не найдено Apple прайсов для тестирования!")
            return
        
        # Тестируем индивидуальные парсеры
        parser_results = self.test_individual_parsers()
        
        # Тестируем гибридный парсер
        hybrid_results = await self.test_hybrid_parser()
        
        # Генерируем отчет
        self.generate_report(parser_results, hybrid_results)

async def main():
    """Главная функция"""
    tester = AppleEcosystemTester()
    await tester.run_full_test()

if __name__ == "__main__":
    asyncio.run(main())
