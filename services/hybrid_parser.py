"""
Система парсинга только на шаблонах с детальным отчетом
"""
import logging
from typing import List, Dict, Any, Tuple
import asyncio
import re

# Импортируем наши специализированные парсеры
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from parsers.iphone_parser import iphone_parser
from parsers.macbook_parser import macbook_parser
from parsers.ipad_parser import iPadParser
from parsers.apple_watch_parser import AppleWatchParser
from parsers.imac_parser import iMacParser
from parsers.airpods_parser import AirPodsParser
from parsers.apple_pencil_parser import ApplePencilParser
from services.iphone_service_simple import iphone_service_simple
from services.macbook_service_simple import macbook_service_simple
from services.ipad_service_simple import ipad_service_simple
from services.apple_watch_service import AppleWatchService
from services.imac_service import iMacService
from services.airpods_service import AirPodsService
from services.apple_pencil_service import ApplePencilService
from services.macbook_service import macbook_service

from bot.database_service_async import db_service

logger = logging.getLogger(__name__)

class TemplateParser:
    """Парсер только на шаблонах с детальным отчетом"""
    
    def __init__(self):
        # Инициализируем новые парсеры
        self.apple_watch_parser = AppleWatchParser()
        self.imac_parser = iMacParser()
        self.airpods_parser = AirPodsParser()
        self.apple_pencil_parser = ApplePencilParser()
        
        # Инициализируем новые сервисы
        self.apple_watch_service = AppleWatchService()
        self.imac_service = iMacService()
        self.airpods_service = AirPodsService()
        self.apple_pencil_service = ApplePencilService()
        
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
                'parser': iPadParser(),
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
            },
            'apple_pencil': {
                'parser': self.apple_pencil_parser,
                'service': self.apple_pencil_service,
                'keywords': ['pencil', '✒️', 'apple pencil'],
                'priority': 7
            }
        }
    
    async def parse_message(self, text: str, source: str = "") -> Dict[str, Any]:
        """
        Парсит сообщение с прайсами только шаблонами с детальным отчетом
        
        Returns:
            Dict с результатами парсинга для каждого типа устройств
        """
        logger.info(f"🔄 Начинаем парсинг только шаблонами ({len(text.split())} слов)")
        
        results = {
            'template_results': {},
            'total_saved': 0,
            'processing_summary': [],
            'unparsed_lines': [],
            'price_like_lines': [],
            'parsed_lines': []
        }
        
        # Разбиваем текст на строки
        lines = text.strip().split('\n')
        processed_lines = set()  # Отслеживаем обработанные строки
        
        # Собираем все строки, которые выглядят как цены
        price_like_lines = self._find_price_like_lines(lines)
        results['price_like_lines'] = price_like_lines
        
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
                            'total_saved': saved_count,
                            'parsed_count': len(parsed_data)
                        }
                    else:
                        # Для других устройств используем стандартный метод
                        source_lines = []
                        for data in parsed_data:
                            if isinstance(data, dict):
                                source_lines.append(data.get('source_line', ''))
                            else:
                                source_lines.append(getattr(data, 'source_line', ''))
                        parse_result = await parser_info['service'].parse_and_save_prices(
                            '\n'.join(source_lines), 
                            source
                        )
                        # Приводим к единому формату
                        if isinstance(parse_result, tuple):
                            parsed_items, saved_count = parse_result
                            save_result = {
                                'total_saved': saved_count,
                                'template_saved': saved_count,
                                'parsed_count': len(parsed_data),
                                'parsed_items': parsed_items
                            }
                        else:
                            save_result = parse_result
                            if 'total_saved' not in save_result:
                                save_result['total_saved'] = save_result.get('saved', 0)
                            if 'template_saved' not in save_result:
                                save_result['template_saved'] = save_result.get('saved', 0)
                            save_result['parsed_count'] = len(parsed_data)
                    
                    results['template_results'][device_type] = save_result
                    results['total_saved'] += save_result['total_saved']
                    
                    # Отмечаем обработанные строки
                    for data in parsed_data:
                        if isinstance(data, dict):
                            line = data.get('source_line', '').strip()
                        else:
                            line = getattr(data, 'source_line', '').strip()
                        processed_lines.add(line)
                        results['parsed_lines'].append(line)
                    
                    results['processing_summary'].append(
                        f"✅ {device_type}: {save_result['template_saved']} сохранено из {save_result['parsed_count']} распознанных"
                    )
                
                # Добавляем нераспознанные строки этого типа в общий список
                results['unparsed_lines'].extend(unparsed_lines)
        
        # Этап 2: Собираем все нераспознанные строки
        remaining_lines = [line for line in lines if line.strip() and line.strip() not in processed_lines]
        results['unparsed_lines'].extend(remaining_lines)
        
        # Генерируем итоговый отчет
        summary = self._generate_detailed_summary(results)
        results['summary'] = summary
        
        logger.info(f"✅ Парсинг шаблонами завершен. Всего сохранено: {results['total_saved']}")
        
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
    
    def _find_price_like_lines(self, lines: List[str]) -> List[str]:
        """Находит строки, которые выглядят как цены"""
        price_like = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Проверяем наличие цены (4-6 цифр или с точками/запятыми)
            has_price = bool(re.search(r'\d{4,6}|\d+[.,]\d+', line))
            
            # Проверяем наличие флага страны
            has_flag = bool(re.search(r'[🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]', line))
            
            # Проверяем наличие GB/TB или других признаков товара
            has_config = bool(re.search(r'(gb|tb|gb|tb|\d+\s*(gb|tb))', line.lower()))
            
            # Исключаем очевидно не товарные строки
            exclude_words = ['гарантия', 'активаций', 'adapter', 'от 10 шт', 'mouse', 'trackpad']
            has_exclude = any(word in line.lower() for word in exclude_words)
            
            if has_price and (has_flag or has_config) and not has_exclude:
                price_like.append(line)
        
        return price_like
    
    def _generate_detailed_summary(self, results: Dict[str, Any]) -> str:
        """Генерирует детальный отчет о парсинге"""
        summary_parts = []
        
        # Общая статистика
        total_price_like = len(results['price_like_lines'])
        total_parsed = len(results['parsed_lines'])
        total_unparsed = len(results['unparsed_lines'])
        total_saved = results['total_saved']
        
        summary_parts.append("📊 **Детальный отчет о парсинге:**")
        summary_parts.append(f"🔍 Найдено строк похожих на цены: **{total_price_like}**")
        summary_parts.append(f"✅ Успешно распознано шаблонами: **{total_parsed}**")
        summary_parts.append(f"💾 Сохранено в базу: **{total_saved}**")
        summary_parts.append(f"❌ Не распознано: **{total_unparsed}**")
        
        # Статистика по устройствам
        if results['processing_summary']:
            summary_parts.append("\n📱 **По типам устройств:**")
            for item in results['processing_summary']:
                summary_parts.append(f"   {item}")
        
        # Показываем нераспознанные строки
        if results['unparsed_lines']:
            summary_parts.append(f"\n❌ **Нераспознанные строки ({len(results['unparsed_lines'])}):**")
            for i, line in enumerate(results['unparsed_lines'][:10], 1):  # Показываем первые 10
                summary_parts.append(f"   {i}. `{line}`")
            if len(results['unparsed_lines']) > 10:
                summary_parts.append(f"   ... и еще {len(results['unparsed_lines']) - 10} строк")
        
        return '\n'.join(summary_parts)

# Создаем глобальный экземпляр
template_parser = TemplateParser()
