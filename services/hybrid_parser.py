"""
Гибридная система парсинга: шаблоны + GPT fallback
"""
import logging
from typing import List, Dict, Any, Tuple
import asyncio

# Импортируем наши специализированные парсеры
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from parsers.iphone_parser import iphone_parser
from parsers.macbook_parser import macbook_parser
from parsers.ipad_parser import ipad_parser
from parsers.apple_watch_parser import AppleWatchParser
from parsers.imac_parser import iMacParser
from parsers.airpods_parser import AirPodsParser
from services.iphone_service_simple import iphone_service_simple
from services.macbook_service_simple import macbook_service_simple
from services.ipad_service_simple import ipad_service_simple
from services.apple_watch_service import AppleWatchService
from services.imac_service import iMacService
from services.airpods_service import AirPodsService
from services.macbook_service import macbook_service

# Импортируем старую систему GPT для fallback
from bot.gptapi import yandex_gpt
from bot.database_service_async import db_service

logger = logging.getLogger(__name__)

class HybridParser:
    """Гибридный парсер: сначала шаблоны, потом GPT"""
    
    def __init__(self):
        # Инициализируем новые парсеры
        self.apple_watch_parser = AppleWatchParser()
        self.imac_parser = iMacParser()
        self.airpods_parser = AirPodsParser()
        
        # Инициализируем новые сервисы
        self.apple_watch_service = AppleWatchService()
        self.imac_service = iMacService()
        self.airpods_service = AirPodsService()
        
        self.device_parsers = {
            'iphone': {
                'parser': iphone_parser,
                'service': iphone_service_simple,
                'keywords': ['iphone', '16e', '16', '15', '14', '13', 'pro', 'plus', 'max'],
                'priority': 1
            },
            'macbook': {
                'parser': macbook_parser,
                'service': macbook_service_simple,
                'keywords': ['macbook', 'air', 'pro', 'm1 ', 'm2 ', 'm3 ', 'm4 '],
                'priority': 2
            },
            'ipad': {
                'parser': ipad_parser,
                'service': ipad_service_simple,
                'keywords': ['ipad', 'mini', 'air', 'pro', 'wifi', 'lte', 'wi-fi'],
                'priority': 3
            },
            'apple_watch': {
                'parser': self.apple_watch_parser,
                'service': self.apple_watch_service,
                'keywords': ['apple watch', 'aw ', 'watch', 'se', 'ultra', 'series', 's10'],
                'priority': 4
            },
            'imac': {
                'parser': self.imac_parser,
                'service': self.imac_service,
                'keywords': ['imac', 'mac mini', 'mini m2', 'mini m4'],
                'priority': 5
            },
            'airpods': {
                'parser': self.airpods_parser,
                'service': self.airpods_service,
                'keywords': ['airpods', '🎧', 'max', 'pro', 'anc', 'lightning', 'usb-c'],
                'priority': 6
            }
        }
    
    async def parse_message(self, text: str, source: str = "") -> Dict[str, Any]:
        """
        Парсит сообщение с прайсами, используя гибридный подход
        
        Returns:
            Dict с результатами парсинга для каждого типа устройств
        """
        logger.info(f"🔄 Начинаем гибридный парсинг сообщения ({len(text.split())} слов)")
        
        results = {
            'template_results': {},
            'gpt_results': {},
            'total_saved': 0,
            'processing_summary': []
        }
        
        # Разбиваем текст на строки
        lines = text.strip().split('\n')
        processed_lines = set()  # Отслеживаем обработанные строки
        
        # Этап 1: Обработка специализированными парсерами (сортировка по приоритету)
        sorted_parsers = sorted(self.device_parsers.items(), key=lambda x: x[1].get('priority', 999))
        for device_type, parser_info in sorted_parsers:
            logger.info(f"📱 Обрабатываем {device_type} шаблонами...")
            
            # Фильтруем строки для этого типа устройства
            device_lines = self._filter_lines_for_device(lines, parser_info['keywords'], device_type)
            
            if device_lines:
                logger.info(f"Найдено {len(device_lines)} потенциальных строк для {device_type}")
                
                # Парсим шаблонами
                parsed_data, unparsed_lines = parser_info['parser'].parse_lines(device_lines)
                
                if parsed_data:
                    # Сохраняем через специализированный сервис
                    if device_type == 'macbook':
                        # Для MacBook используем специальный метод
                        saved_count = 0
                        for data in parsed_data:
                            price_data = data.to_dict()
                            price_data['source'] = source
                            result = await parser_info['service'].save_macbook_price(price_data)
                            if result:
                                saved_count += 1
                        
                        save_result = {
                            'template_saved': saved_count,
                            'total_saved': saved_count
                        }
                    else:
                        # Для других устройств используем стандартный метод
                        source_lines = []
                        for data in parsed_data:
                            if isinstance(data, dict):
                                source_lines.append(data.get('source_line', ''))
                            else:
                                source_lines.append(getattr(data, 'source_line', ''))
                        save_result = await parser_info['service'].parse_and_save_prices(
                            '\n'.join(source_lines), 
                            source
                        )
                        # Приводим к единому формату
                        if 'total_saved' not in save_result:
                            save_result['total_saved'] = save_result.get('saved', 0)
                        if 'template_saved' not in save_result:
                            save_result['template_saved'] = save_result.get('saved', 0)
                    
                    results['template_results'][device_type] = save_result
                    results['total_saved'] += save_result['total_saved']
                    
                    # Отмечаем обработанные строки
                    for data in parsed_data:
                        if isinstance(data, dict):
                            processed_lines.add(data.get('source_line', '').strip())
                        else:
                            processed_lines.add(getattr(data, 'source_line', '').strip())
                    
                    results['processing_summary'].append(
                        f"✅ {device_type}: {save_result['template_saved']} шаблонами"
                    )
                
                # Если есть нераспознанные строки этого типа, отправляем в GPT с специализированным промптом
                if unparsed_lines:
                    logger.info(f"📤 Отправляем {len(unparsed_lines)} нераспознанных {device_type} строк в GPT")
                    
                    gpt_text = '\n'.join(unparsed_lines)
                    gpt_parsed = await yandex_gpt.parse_prices(gpt_text, device_type)
                    
                    if gpt_parsed:
                        gpt_saved = 0
                        
                        # Для MacBook и iPad используем специализированные сервисы
                        if device_type == 'macbook':
                            for item in gpt_parsed:
                                result = await macbook_service_simple.save_macbook_price(item)
                                if result:
                                    gpt_saved += 1
                        elif device_type == 'ipad':
                            for item in gpt_parsed:
                                result = await ipad_service_simple.save_ipad_price(item)
                                if result:
                                    gpt_saved += 1
                        elif device_type == 'apple_watch':
                            for item in gpt_parsed:
                                result = await apple_watch_service_simple.save_apple_watch_price(item)
                                if result:
                                    gpt_saved += 1
                        else:
                            # Для других устройств используем общий сервис
                            gpt_saved = await db_service.process_parsed_prices(gpt_parsed, f"GPT-{device_type}")
                        
                        if device_type not in results['gpt_results']:
                            results['gpt_results'][device_type] = {'saved': 0, 'parsed': 0}
                        
                        results['gpt_results'][device_type]['parsed'] += len(gpt_parsed)
                        results['gpt_results'][device_type]['saved'] += gpt_saved
                        results['total_saved'] += gpt_saved
                        
                        results['processing_summary'].append(
                            f"🤖 {device_type}: {gpt_saved} через GPT"
                        )
                        
                        # Отмечаем как обработанные
                        for line in unparsed_lines:
                            processed_lines.add(line.strip())
        
        # Этап 2: Оставшиеся строки отправляем в общий GPT
        remaining_lines = [line for line in lines if line.strip() and line.strip() not in processed_lines]
        
        if remaining_lines:
            logger.info(f"📤 Отправляем {len(remaining_lines)} оставшихся строк в общий GPT")
            
            remaining_text = '\n'.join(remaining_lines)
            gpt_parsed = await yandex_gpt.parse_prices(remaining_text)
            
            if gpt_parsed:
                # Фильтруем товары по типам и обрабатываем их через специализированные сервисы
                macbook_items = [item for item in gpt_parsed if item.get('device', '').lower() == 'macbook' and item.get('firm', '').lower() == 'apple']
                ipad_items = [item for item in gpt_parsed if item.get('device', '').lower().startswith('ipad') and item.get('firm', '').lower() == 'apple']
                apple_watch_items = [item for item in gpt_parsed if item.get('device', '').lower() == 'apple watch' and item.get('firm', '').lower() == 'apple']
                imac_items = [item for item in gpt_parsed if item.get('device', '').lower() in ['imac', 'mac mini'] and item.get('firm', '').lower() == 'apple']
                airpods_items = [item for item in gpt_parsed if item.get('device', '').lower() == 'airpods' and item.get('firm', '').lower() == 'apple']
                other_items = [item for item in gpt_parsed if not (
                    (item.get('device', '').lower() == 'macbook' and item.get('firm', '').lower() == 'apple') or
                    (item.get('device', '').lower().startswith('ipad') and item.get('firm', '').lower() == 'apple') or
                    (item.get('device', '').lower() == 'apple watch' and item.get('firm', '').lower() == 'apple') or
                    (item.get('device', '').lower() in ['imac', 'mac mini'] and item.get('firm', '').lower() == 'apple') or
                    (item.get('device', '').lower() == 'airpods' and item.get('firm', '').lower() == 'apple')
                )]
                
                gpt_saved = 0
                
                # Обрабатываем MacBook товары через специализированный сервис
                if macbook_items:
                    logger.info(f"Обрабатываем {len(macbook_items)} MacBook товаров через специализированный сервис")
                    for item in macbook_items:
                        result = await macbook_service_simple.save_macbook_price(item)
                        if result:
                            gpt_saved += 1
                
                # Обрабатываем iPad товары через специализированный сервис
                if ipad_items:
                    logger.info(f"Обрабатываем {len(ipad_items)} iPad товаров через специализированный сервис")
                    for item in ipad_items:
                        result = await ipad_service_simple.save_ipad_price(item)
                        if result:
                            gpt_saved += 1
                
                # Обрабатываем Apple Watch товары через специализированный сервис
                if apple_watch_items:
                    logger.info(f"Обрабатываем {len(apple_watch_items)} Apple Watch товаров через специализированный сервис")
                    for item in apple_watch_items:
                        result = await self.apple_watch_service.save_apple_watch_price(item)
                        if result:
                            gpt_saved += 1
                
                # Обрабатываем iMac товары через специализированный сервис
                if imac_items:
                    logger.info(f"Обрабатываем {len(imac_items)} iMac товаров через специализированный сервис")
                    for item in imac_items:
                        result = await self.imac_service.save_imac_price(item)
                        if result:
                            gpt_saved += 1
                
                # Обрабатываем AirPods товары через специализированный сервис
                if airpods_items:
                    logger.info(f"Обрабатываем {len(airpods_items)} AirPods товаров через специализированный сервис")
                    for item in airpods_items:
                        result = await self.airpods_service.save_airpods_price(item)
                        if result:
                            gpt_saved += 1
                
                # Обрабатываем остальные товары через общий сервис
                if other_items:
                    other_saved = await db_service.process_parsed_prices(other_items, "GPT-общий")
                    gpt_saved += other_saved
                
                results['gpt_results']['general'] = {
                    'parsed': len(gpt_parsed),
                    'saved': gpt_saved
                }
                results['total_saved'] += gpt_saved
                
                results['processing_summary'].append(f"🤖 Общий GPT: {gpt_saved} товаров")
        
        # Генерируем итоговый отчет
        summary = self._generate_summary(results)
        results['summary'] = summary
        
        logger.info(f"✅ Гибридный парсинг завершен. Всего сохранено: {results['total_saved']}")
        
        return results
    
    def _filter_lines_for_device(self, lines: List[str], keywords: List[str], device_type: str = None) -> List[str]:
        """Фильтрует строки для конкретного типа устройства"""
        filtered_lines = []
        
        for line in lines:
            line_lower = line.lower()
            
            # Проверяем наличие ключевых слов
            has_keyword = any(keyword in line_lower for keyword in keywords)
            
            # Для строк с флагами, проверяем наличие устройства более строго
            if self._has_flag(line) and device_type:
                if device_type == 'ipad' and 'ipad' in line_lower:
                    has_keyword = True
                elif device_type == 'iphone' and ('iphone' in line_lower or any(k in line_lower for k in ['13', '14', '15', '16', 'pro', 'plus', 'max'])):
                    has_keyword = True
                elif device_type == 'macbook' and 'macbook' in line_lower:
                    has_keyword = True
            
            if has_keyword:
                # Дополнительные проверки для качества
                if (self._has_price(line) and 
                    not self._is_exclude_line(line)):
                    
                    # Специальные проверки для MacBook - исключаем iPhone строки
                    if device_type == 'macbook':
                        # Если строка содержит iPhone-специфичные паттерны, пропускаем
                        if self._is_iphone_line(line):
                            continue
                        # Дополнительная проверка - MacBook должен содержать слово "MacBook" или специфичные чипы
                        if not self._is_macbook_line(line):
                            continue
                    
                    filtered_lines.append(line)
        
        return filtered_lines
    
    def _has_price(self, line: str) -> bool:
        """Проверяет наличие цены в строке"""
        import re
        return bool(re.search(r'\d{4,6}', line))
    
    def _has_flag(self, line: str) -> bool:
        """Проверяет наличие флага страны"""
        import re
        return bool(re.search(r'[🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]', line))
    
    def _is_iphone_line(self, line: str) -> bool:
        """Проверяет, является ли строка iPhone строкой"""
        import re
        line_lower = line.lower()
        
        # iPhone-специфичные паттерны
        iphone_patterns = [
            r'\b(13|14|15|16)\s+(128|256|512|1tb)\s+',  # iPhone 13 128GB
            r'\b(13|14|15|16)\s+(plus|pro|max)\s+',     # iPhone 16 Pro
            r'\b(13|14|15|16)\s+(black|white|blue|green|pink|starlight|midnight|natural|desert|ultramarine|teal)\s+',  # iPhone с цветами
            r'\b(13|14|15|16)e\s+',  # iPhone 16E
            r'iphone\s+',  # Слово iPhone
        ]
        
        for pattern in iphone_patterns:
            if re.search(pattern, line_lower):
                return True
        
        return False
    
    def _is_macbook_line(self, line: str) -> bool:
        """Проверяет, является ли строка MacBook строкой"""
        import re
        line_lower = line.lower()
        
        # MacBook-специфичные паттерны
        macbook_patterns = [
            r'macbook\s+',  # Слово MacBook
            r'\bm[1-4]\s+',  # Чипы M1, M2, M3, M4
            r'\bm[1-4]\s+max\s+',  # Чипы M1 Max, M4 Max
            r'\b(air|pro)\s+',  # Air, Pro
        ]
        
        for pattern in macbook_patterns:
            if re.search(pattern, line_lower):
                return True
        
        return False
    
    def _is_exclude_line(self, line: str) -> bool:
        """Проверяет, нужно ли исключить строку"""
        exclude_words = ['гарантия', 'активаций', 'adapter', 'от 10 шт']
        line_lower = line.lower()
        return any(word in line_lower for word in exclude_words)
    
    def _generate_summary(self, results: Dict[str, Any]) -> str:
        """Генерирует итоговый отчет"""
        summary_parts = []
        
        if results['processing_summary']:
            summary_parts.append("📊 Результаты обработки:")
            for item in results['processing_summary']:
                summary_parts.append(f"   {item}")
        
        summary_parts.append(f"\n✅ Всего сохранено: {results['total_saved']} товаров")
        
        # Детальная статистика
        template_total = sum(r.get('total_saved', 0) for r in results['template_results'].values())
        gpt_total = sum(r.get('saved', 0) for r in results['gpt_results'].values())
        
        if template_total > 0:
            summary_parts.append(f"🎯 Шаблонами: {template_total}")
        if gpt_total > 0:
            summary_parts.append(f"🤖 GPT: {gpt_total}")
        
        return '\n'.join(summary_parts)

# Создаем глобальный экземпляр
hybrid_parser = HybridParser()
