"""
Гибкий парсер для iPhone с шаблонами
"""
import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class IPhonePriceData:
    """Структура данных для цены iPhone"""
    generation: str  # 13, 14, 15, 16, 16E
    variant: str  # "", Plus, Pro, Pro Max
    storage: str  # 128GB, 256GB, 512GB, 1TB
    color: str  # Black, White, Blue, etc.
    country_flag: str  # 🇺🇸, 🇯🇵, etc.
    country_code: str  # 2SIM, etc.
    price: int
    source_line: str  # Исходная строка для отладки

class IPhoneParser:
    """Парсер для iPhone с гибкими шаблонами"""
    
    def __init__(self):
        self.patterns = self._create_patterns()
        self.colors = self._get_color_mappings()
        self.countries = self._get_country_mappings()
        
    def _create_patterns(self) -> List[Dict]:
        """Создает шаблоны для разных форматов iPhone"""
        return [
            # Формат: 🇺🇸16 128 White - 58900
            {
                'pattern': r'([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]+)(\d{1,2}[A-Z]?)\s+(\d+(?:GB|TB)?)\s+([A-Za-z\s]+?)\s*-\s*(\d+)',
                'groups': ['country', 'generation', 'storage', 'color', 'price'],
                'variant': ''
            },
            # Формат: 13 128 Midnight - 38000🇮🇳
            {
                'pattern': r'(\d{1,2}[A-Z]?)\s+(\d+(?:GB|TB)?)\s+([A-Za-z\s]+?)\s*-\s*(\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]+)',
                'groups': ['generation', 'storage', 'color', 'price', 'country'],
                'variant': ''
            },
            # Формат: 16 128 White 🇮🇳 58900
            {
                'pattern': r'(\d{1,2}[A-Z]?)\s+(\d+(?:GB|TB)?)\s+([A-Za-z\s]+?)\s+([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]+)\s+(\d+)',
                'groups': ['generation', 'storage', 'color', 'country', 'price'],
                'variant': ''
            },
            # Формат: 15Pro 128 Blue - 78500🇦🇪
            {
                'pattern': r'(\d{1,2}[A-Z]?)(Plus|Pro Max|Pro)\s+(\d+(?:GB|TB)?)\s+([A-Za-z\s]+?)\s*-\s*(\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]+)',
                'groups': ['generation', 'variant', 'storage', 'color', 'price', 'country'],
                'variant': 'from_match'
            },
            # Формат: 16 Pro 128 Black 87300🇯🇵 (с пробелом, флаг в конце)
            {
                'pattern': r'(\d{1,2}[A-Z]?)\s+(Plus|Pro Max|Pro)\s+(\d+(?:GB|TB)?)\s+([A-Za-z\s]+?)\s+(\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳🇦🇺]+)(?:[A-Za-z0-9]*)?',
                'groups': ['generation', 'variant', 'storage', 'color', 'price', 'country'],
                'variant': 'from_match'
            },
            # Формат: 16 Plus 128 Teal 🇮🇳 60200
            {
                'pattern': r'(\d{1,2}[A-Z]?)\s+(Plus|Pro Max|Pro)\s+(\d+(?:GB|TB)?)\s+([A-Za-z\s]+?)\s+([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]+)\s+(\d+)',
                'groups': ['generation', 'variant', 'storage', 'color', 'country', 'price'],
                'variant': 'from_match'
            },
            # Формат: 🇦🇪15 Pro 128 Blue - 76000
            {
                'pattern': r'([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]+)(\d{1,2}[A-Z]?)\s+(Plus|Pro Max|Pro)\s+(\d+(?:GB|TB)?)\s+([A-Za-z\s]+?)\s*-\s*(\d+)',
                'groups': ['country', 'generation', 'variant', 'storage', 'color', 'price'],
                'variant': 'from_match'
            },
            # Формат: 16E 128 Black 🇮🇳 42800
            {
                'pattern': r'(\d{1,2}[A-Z]+)\s+(\d+(?:GB|TB)?)\s+([A-Za-z\s]+?)\s+([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]+)\s+(\d+)',
                'groups': ['generation', 'storage', 'color', 'country', 'price'],
                'variant': ''
            },
            # Формат: 🇨🇳16 Pro 128 Black - 79500
            {
                'pattern': r'([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]+)(\d{1,2}[A-Z]?)\s+(Plus|Pro Max|Pro)\s+(\d+(?:GB|TB)?)\s+([A-Za-z\s]+?)\s*-\s*(\d+)',
                'groups': ['country', 'generation', 'variant', 'storage', 'color', 'price'],
                'variant': 'from_match'
            },
            # Формат с 2SIM: 🇨🇳16Pro 128 Black - 80500🇨🇳2Sim
            {
                'pattern': r'([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]+)(\d{1,2}[A-Z]?)(Plus|Pro Max|Pro)?\s+(\d+(?:GB|TB)?)\s+([A-Za-z\s]+?)\s*-\s*(\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]+)?(2Sim|2SIM)?',
                'groups': ['country', 'generation', 'variant', 'storage', 'color', 'price', 'country2', 'sim_code'],
                'variant': 'from_match'
            },
            # Формат с GB в памяти: 14 128GB Midnight 2Sim 🇨🇳 43200
            {
                'pattern': r'(\d{1,2}[A-Z]?)\s+(\d+(?:GB|TB))\s+([A-Za-z\s]+?)\s+(2Sim|2SIM)?\s*([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]+)\s+(\d+)',
                'groups': ['generation', 'storage', 'color', 'sim_code', 'country', 'price'],
                'variant': ''
            },
            # Формат без пробела перед флагом: 13 128 Midnight 38500🇮🇳
            {
                'pattern': r'(\d{1,2}[A-Z]?)\s+(\d+(?:GB|TB)?)\s+([A-Za-z\s]+?)\s+(\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]+)',
                'groups': ['generation', 'storage', 'color', 'price', 'country'],
                'variant': ''
            },
            # Формат Apple iPhone: Apple iPhone 11 64GB Black 27100🇷🇺
            {
                'pattern': r'Apple iPhone\s+(\d{1,2}[A-Z]?)\s+(\d+(?:GB|TB))\s+([A-Za-z\s]+?)\s+(\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]+)',
                'groups': ['generation', 'storage', 'color', 'price', 'country'],
                'variant': ''
            },
            # Формат Apple iPhone с вариантом: Apple iPhone 16 Pro 128GB Black 2SIM 80000🇨🇳
            {
                'pattern': r'Apple iPhone\s+(\d{1,2}[A-Z]?)\s+(Plus|Pro Max|Pro)\s+(\d+(?:GB|TB))\s+([A-Za-z\s]+?)\s+(2Sim|2SIM)?\s*(\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]+)',
                'groups': ['generation', 'variant', 'storage', 'color', 'sim_code', 'price', 'country'],
                'variant': 'from_match'
            },
            # Формат с тире и эмодзи: 14 128 Black 2 Sim 🇨🇳 - 43.300🚘
            {
                'pattern': r'(\d{1,2}[A-Z]?)\s+(\d+(?:GB|TB)?)\s+([A-Za-z\s]+?)\s+(2\s*Sim|2Sim|2SIM)?\s*([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]+)\s*-\s*(\d+[.,]\d+|\d+)[🚘🚚]?',
                'groups': ['generation', 'storage', 'color', 'sim_code', 'country', 'price'],
                'variant': ''
            },
            # Формат с 2Sim в конце: 16 Pro 128GB Black 2Sim 🇨🇳 81000
            {
                'pattern': r'(\d{1,2}[A-Z]?)\s+(Plus|Pro Max|Pro)\s+(\d+(?:GB|TB))\s+([A-Za-z\s]+?)\s+(2Sim|2SIM)\s*([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]+)\s+(\d+)',
                'groups': ['generation', 'variant', 'storage', 'color', 'sim_code', 'country', 'price'],
                'variant': 'from_match'
            },
            # Формат с 2Sim в конце без варианта: 14 128GB Midnight 2Sim 🇨🇳 43200
            {
                'pattern': r'(\d{1,2}[A-Z]?)\s+(\d+(?:GB|TB))\s+([A-Za-z\s]+?)\s+(2Sim|2SIM)\s*([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]+)\s+(\d+)',
                'groups': ['generation', 'storage', 'color', 'sim_code', 'country', 'price'],
                'variant': ''
            },
            # Формат с эмодзи в конце: 16 Pro 128GB Black 2Sim 🇨🇳 81000 🚚
            {
                'pattern': r'(\d{1,2}[A-Z]?)\s+(Plus|Pro Max|Pro)\s+(\d+(?:GB|TB))\s+([A-Za-z\s]+?)\s+(2Sim|2SIM)\s*([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]+)\s+(\d+)\s*[🚘🚚]?',
                'groups': ['generation', 'variant', 'storage', 'color', 'sim_code', 'country', 'price'],
                'variant': 'from_match'
            },
            # Формат Apple iPhone с пробелами: Apple iPhone 11 64GB Black  27100🇷🇺
            {
                'pattern': r'Apple iPhone\s+(\d{1,2}[A-Z]?)\s+(\d+(?:GB|TB))\s+([A-Za-z\s]+?)\s+(\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]+)',
                'groups': ['generation', 'storage', 'color', 'price', 'country'],
                'variant': ''
            },
            # Формат Apple iPhone с 2SIM: Apple iPhone 14 128GB Starlight 2SIM  42000🇨🇳
            {
                'pattern': r'Apple iPhone\s+(\d{1,2}[A-Z]?)\s+(\d+(?:GB|TB))\s+([A-Za-z\s]+?)\s+(2Sim|2SIM)\s+(\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]+)',
                'groups': ['generation', 'storage', 'color', 'sim_code', 'price', 'country'],
                'variant': ''
            },
            # Формат Apple iPhone с пробелами: Apple iPhone 11 64GB Black  27100🇷🇺
            {
                'pattern': r'Apple iPhone\s+(\d{1,2}[A-Z]?)\s+(\d+(?:GB|TB))\s+([A-Za-z\s]+?)\s+(\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]+)',
                'groups': ['generation', 'storage', 'color', 'price', 'country'],
                'variant': ''
            },
            # Формат Apple iPhone с пробелами (без GB): Apple iPhone 11 64 Black  27100🇷🇺
            {
                'pattern': r'Apple iPhone\s+(\d{1,2}[A-Z]?)\s+(\d+)\s+([A-Za-z\s]+?)\s+(\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]+)',
                'groups': ['generation', 'storage', 'color', 'price', 'country'],
                'variant': ''
            },
            # Формат с тире и эмодзи: 14 128 Black 2 Sim 🇨🇳 - 43.300🚘
            {
                'pattern': r'(\d{1,2}[A-Z]?)\s+(\d+(?:GB|TB)?)\s+([A-Za-z\s]+?)\s+(2\s*Sim|2Sim|2SIM)\s*([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]+)\s*-\s*(\d+[.,]\d+|\d+)[🚘🚚]?',
                'groups': ['generation', 'storage', 'color', 'sim_code', 'country', 'price'],
                'variant': ''
            }
        ]
    
    def _get_color_mappings(self) -> Dict[str, str]:
        """Маппинг цветов для нормализации"""
        return {
            # Основные цвета
            'black': 'Black',
            'white': 'White', 
            'blue': 'Blue',
            'green': 'Green',
            'red': 'Red',
            'pink': 'Pink',
            'purple': 'Purple',
            'yellow': 'Yellow',
            'orange': 'Orange',
            
            # Специальные цвета iPhone
            'midnight': 'Midnight',
            'starlight': 'Starlight',
            'natural': 'Natural',
            'desert': 'Desert',
            'ultramarine': 'Ultramarine',
            'teal': 'Teal',
            
            # Pro цвета
            'titan': 'Titanium',
            'titanium': 'Titanium',
            'space gray': 'Space Gray',
            'space grey': 'Space Gray',
            'graphite': 'Graphite',
            'gold': 'Gold',
            'rose gold': 'Rose Gold',
            'silver': 'Silver'
        }
    
    def _get_country_mappings(self) -> Dict[str, str]:
        """Маппинг стран"""
        return {
            '🇺🇸': 'США',
            '🇯🇵': 'Япония', 
            '🇮🇳': 'Индия',
            '🇨🇳': 'Китай',
            '🇦🇪': 'ОАЭ',
            '🇭🇰': 'Гонконг',
            '🇰🇷': 'Южная Корея',
            '🇪🇺': 'Европа',
            '🇷🇺': 'Россия',
            '🇨🇦': 'Канада',
            '🇻🇳': 'Вьетнам'
        }
    
    def parse_lines(self, lines: List[str]) -> Tuple[List[IPhonePriceData], List[str]]:
        """
        Парсит строки с iPhone ценами
        
        Returns:
            Tuple[успешно распарсенные, нераспознанные строки]
        """
        parsed = []
        unparsed = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Проверяем, что это строка с iPhone
            if not self._is_iphone_line(line):
                continue
                
            result = self._parse_single_line(line)
            if result:
                parsed.append(result)
            else:
                unparsed.append(line)
                
        return parsed, unparsed
    
    def _is_iphone_line(self, line: str) -> bool:
        """Проверяет, что строка содержит информацию об iPhone"""
        line_lower = line.lower()
        
        # Должен содержать признаки iPhone цены
        has_generation = bool(re.search(r'(11|12|13|14|15|16|16e)', line_lower))
        has_storage = bool(re.search(r'(128|256|512|1tb|\b\d+\s*(gb|tb))', line_lower))  # Добавили конкретные объемы
        has_price = bool(re.search(r'\d{4,6}|\d+[.,]\d+', line))  # Добавили поддержку цен с точкой/запятой
        has_flag = bool(re.search(r'[🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]', line))
        
        # Дополнительная проверка для Apple iPhone строк
        has_apple_iphone = bool(re.search(r'apple\s+iphone', line_lower))
        
        # Исключаем очевидно не iPhone строки
        exclude_words = ['ipad', 'macbook', 'airpods', 'watch', 'adapter', 'гарантия', 'активаций', 'aw ', 'ultra 2', 'mini 7', 'pro 11']
        has_exclude = any(word in line_lower for word in exclude_words)
        
        # Для Apple iPhone строк нужны только generation, price и flag
        if has_apple_iphone:
            return has_generation and has_price and has_flag and not has_exclude
        
        # Для обычных iPhone строк нужны все признаки
        return has_generation and has_storage and has_price and has_flag and not has_exclude
    
    def _parse_single_line(self, line: str) -> Optional[IPhonePriceData]:
        """Парсит одну строку"""
        for pattern_info in self.patterns:
            match = re.search(pattern_info['pattern'], line, re.IGNORECASE)
            if match:
                try:
                    return self._extract_data_from_match(match, pattern_info, line)
                except Exception as e:
                    logger.warning(f"Ошибка извлечения данных из строки '{line}': {e}")
                    continue
        
        return None
    
    def _extract_data_from_match(self, match, pattern_info: Dict, line: str) -> IPhonePriceData:
        """Извлекает данные из regex match"""
        groups = pattern_info['groups']
        data = {}
        
        # Извлекаем данные по группам
        for i, group_name in enumerate(groups, 1):
            if i <= len(match.groups()):
                data[group_name] = match.group(i)
        
        # Нормализуем данные
        generation = self._normalize_generation(data.get('generation', ''))
        variant = self._normalize_variant(data.get('variant', ''), pattern_info.get('variant', ''))
        storage = self._normalize_storage(data.get('storage', ''))
        color = self._normalize_color(data.get('color', ''))
        country_flag = data.get('country', data.get('country2', '🇺🇸'))
        country_code = data.get('sim_code', '')
        
        # Обрабатываем цену с запятыми/точками как разделителями тысяч
        price_str = data.get('price', '0')
        if ',' in price_str or '.' in price_str:
            price_str = price_str.replace(',', '').replace('.', '')
        price = int(price_str)
        
        return IPhonePriceData(
            generation=generation,
            variant=variant,
            storage=storage,
            color=color,
            country_flag=country_flag,
            country_code=country_code,
            price=price,
            source_line=line
        )
    
    def _normalize_generation(self, gen: str) -> str:
        """Нормализует поколение iPhone"""
        gen = gen.strip().upper()
        if gen in ['16E', '16Е']:  # Русская Е
            return '16E'
        return gen
    
    def _normalize_variant(self, variant: str, variant_type: str) -> str:
        """Нормализует вариант iPhone"""
        if variant_type == 'from_match' and variant:
            variant = variant.strip()
            if variant.lower() == 'pro max':
                return 'Pro Max'
            elif variant.lower() == 'pro':
                return 'Pro'
            elif variant.lower() == 'plus':
                return 'Plus'
        return ''
    
    def _normalize_storage(self, storage: str) -> str:
        """Нормализует объем памяти"""
        storage = storage.strip().upper()
        if not storage.endswith(('GB', 'TB')):
            storage += 'GB'
        return storage
    
    def _normalize_color(self, color: str) -> str:
        """Нормализует цвет"""
        color = color.strip().lower()
        return self.colors.get(color, color.title())

# Создаем глобальный экземпляр парсера
iphone_parser = IPhoneParser()
