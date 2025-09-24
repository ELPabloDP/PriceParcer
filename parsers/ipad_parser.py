"""
Новый упрощенный парсер для iPad
"""
import re
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class iPadData:
    """Данные iPad"""
    generation: str
    variant: str = ""
    size: str = ""
    storage: str = ""
    color: str = ""
    connectivity: str = ""
    product_code: str = ""
    country: str = ""
    price: int = 0
    source_line: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Конвертирует в словарь для сохранения"""
        return {
            'firm': 'Apple',
            'device': 'iPad',
            'generation': self.generation,
            'variant': self.variant,
            'size': self.size,
            'storage': self.storage,
            'color': self.color,
            'connectivity': self.connectivity,
            'product_code': self.product_code,
            'country': self.country,
            'price': self.price
        }

class iPadParser:
    """Новый упрощенный парсер для iPad"""
    
    def __init__(self):
        # Простые и эффективные паттерны
        self.patterns = [
            # 1. iPad Mini 7 256GB Blue Wi-Fi 42800
            {
                'pattern': r'iPad\s+Mini\s+(\d+)\s+(\d+GB?)\s+(\w+(?:\s+\w+)*)\s+(Wi-Fi|LTE|WiFi)\s+(\d+)',
                'groups': ['generation', 'storage', 'color', 'connectivity', 'price'],
                'variant': 'Mini'
            },
            # 2. iPad Air 11 M3 128GB Blue Wi-Fi 42500
            {
                'pattern': r'iPad\s+Air\s+(\d+)\s+(M\d+)\s+(\d+GB?)\s+(\w+(?:\s+\w+)*)\s+(Wi-Fi|LTE|WiFi)\s+(\d+)',
                'groups': ['generation', 'chip', 'storage', 'color', 'connectivity', 'price'],
                'variant': 'Air'
            },
            # 3. iPad Pro 11 M4 256GB Black LTE 112000
            {
                'pattern': r'iPad\s+Pro\s+(\d+)\s+(M\d+)\s+(\d+GB?)\s+(\w+(?:\s+\w+)*)\s+(Wi-Fi|LTE|WiFi)\s+(\d+)',
                'groups': ['generation', 'chip', 'storage', 'color', 'connectivity', 'price'],
                'variant': 'Pro'
            },
            # 4. iPad 9 64GB Gray LTE 24500
            {
                'pattern': r'iPad\s+(\d+)\s+(\d+GB?)\s+(\w+(?:\s+\w+)*)\s+(Wi-Fi|LTE|WiFi)\s+(\d+)',
                'groups': ['generation', 'storage', 'color', 'connectivity', 'price'],
                'variant': ''
            },
            # 5. iPad Mini 7 256 Starlight WiFi- 43000🇺🇸
            {
                'pattern': r'iPad\s+Mini\s+(\d+)\s+(\d+)\s+(\w+(?:\s+\w+)*)\s+(WiFi|Wi-Fi|LTE)[-–]\s*(\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]*)',
                'groups': ['generation', 'storage', 'color', 'connectivity', 'price', 'country'],
                'variant': 'Mini'
            },
            # 6. iPad Air 11 M3 (2025) 128 Blue Wi-Fi 42500
            {
                'pattern': r'iPad\s+Air\s+(\d+)\s+(M\d+)\s*\([^)]+\)\s+(\d+)\s+(\w+(?:\s+\w+)*)\s+(Wi-Fi|WiFi|LTE)\s+(\d+)',
                'groups': ['generation', 'chip', 'storage', 'color', 'connectivity', 'price'],
                'variant': 'Air'
            },
            # 7. iPad 11 (2025) 128 Blue WiFi - 31500🇺🇸
            {
                'pattern': r'iPad\s+(\d+)\s*\([^)]+\)\s+(\d+)\s+(\w+(?:\s+\w+)*)\s+(WiFi|Wi-Fi|LTE)\s*[-–]\s*(\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]*)',
                'groups': ['generation', 'storage', 'color', 'connectivity', 'price', 'country'],
                'variant': ''
            },
            # 8. iPad 10 64 Silver LTE - 33.000
            {
                'pattern': r'iPad\s+(\d+)\s+(\d+)\s+(\w+(?:\s+\w+)*)\s+(LTE|WiFi|Wi-Fi)\s*[-–]\s*([\d.,]+)',
                'groups': ['generation', 'storage', 'color', 'connectivity', 'price'],
                'variant': ''
            },
            # 9. Apple iPad Air 11 M3 Wi-Fi 128GB Blue 42500🇺🇸
            {
                'pattern': r'Apple\s+iPad\s+Air\s+(\d+)\s+(M\d+)\s+(Wi-Fi|WiFi|LTE)\s+(\d+GB?)\s+(\w+(?:\s+\w+)*)\s+(\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]*)',
                'groups': ['generation', 'chip', 'connectivity', 'storage', 'color', 'price', 'country'],
                'variant': 'Air'
            },
            # 10. MINI 7 256 Blue Wi-Fi 🇺🇸 43000
            {
                'pattern': r'MINI\s+(\d+)\s+(\d+)\s+(\w+(?:\s+\w+)*)\s+(Wi-Fi|WiFi|LTE)\s+([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]*)\s+(\d+)',
                'groups': ['generation', 'storage', 'color', 'connectivity', 'country', 'price'],
                'variant': 'Mini'
            },
            # 11. iPad Air 11 M3 (2025) 128 Gray WiFi - 44500🇺🇸
            {
                'pattern': r'iPad\s+Air\s+(\d+)\s+(M\d+)\s*\([^)]+\)\s+(\d+)\s+(\w+(?:\s+\w+)*)\s+(WiFi|Wi-Fi|LTE)\s*[-–]\s*([\d.,]+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]*)',
                'groups': ['generation', 'chip', 'storage', 'color', 'connectivity', 'price', 'country'],
                'variant': 'Air'
            },
            # 12. iPad Mini 7 256 Wi-Fi Starlight 44100🇺🇸
            {
                'pattern': r'iPad\s+Mini\s+(\d+)\s+(\d+)\s+(Wi-Fi|WiFi|LTE)\s+(\w+(?:\s+\w+)*)\s+(\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]*)',
                'groups': ['generation', 'storage', 'connectivity', 'color', 'price', 'country'],
                'variant': 'Mini'
            },
            # 13. iPad Pro 11 M4 256 Black LTE - 95.000
            {
                'pattern': r'iPad\s+Pro\s+(\d+)\s+(M\d+)\s+(\d+)\s+(\w+(?:\s+\w+)*)\s+(LTE|Wi-Fi|WiFi)\s*[-–]\s*([\d.,]+)',
                'groups': ['generation', 'chip', 'storage', 'color', 'connectivity', 'price'],
                'variant': 'Pro'
            },
            # 14. iPad 11 128 Pink Wi-Fi 🇺🇸 31800
            {
                'pattern': r'iPad\s+(\d+)\s+(\d+)\s+(\w+(?:\s+\w+)*)\s+(Wi-Fi|WiFi|LTE)\s+([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]*)\s+(\d+)',
                'groups': ['generation', 'storage', 'color', 'connectivity', 'country', 'price'],
                'variant': ''
            },
            # 15. iPad Air 11 128GB Blue Wi-Fi M3 (2025) M3 42500
            {
                'pattern': r'iPad\s+Air\s+(\d+)\s+(\d+GB?)\s+(\w+(?:\s+\w+)*)\s+(Wi-Fi|WiFi|LTE)\s+(M\d+)\s*\([^)]+\)\s+(M\d+)\s+(\d+)',
                'groups': ['generation', 'storage', 'color', 'connectivity', 'chip', 'chip2', 'price'],
                'variant': 'Air'
            },
            # 16. iPad Pro 13 1TB Space Black LTE (2024) M4 137000
            {
                'pattern': r'iPad\s+Pro\s+(\d+)\s+(\d+GB?)\s+(\w+(?:\s+\w+)*)\s+(LTE|Wi-Fi|WiFi)\s*\([^)]+\)\s+(M\d+)\s+(\d+)',
                'groups': ['generation', 'storage', 'color', 'connectivity', 'chip', 'price'],
                'variant': 'Pro'
            },
            # 17. iPad Mini 2024 128 Black LTE - 53.000
            {
                'pattern': r'iPad\s+Mini\s+(\d{4})\s+(\d+)\s+(\w+(?:\s+\w+)*)\s+(LTE|Wi-Fi|WiFi)\s*[-–]\s*([\d.,]+)',
                'groups': ['year', 'storage', 'color', 'connectivity', 'price'],
                'variant': 'Mini'
            },
            # 18. iPad Air 11 2024 128 Blue LTE - 54.000
            {
                'pattern': r'iPad\s+Air\s+(\d+)\s+(\d{4})\s+(\d+)\s+(\w+(?:\s+\w+)*)\s+(LTE|Wi-Fi|WiFi)\s*[-–]\s*([\d.,]+)',
                'groups': ['generation', 'year', 'storage', 'color', 'connectivity', 'price'],
                'variant': 'Air'
            },
        # 19. iPad Pro 11 M4 1TB Black Wi-Fi - 136.000
        {
            'pattern': r'iPad\s+Pro\s+(\d+)\s+(M\d+)\s+(\d+GB?)\s+(\w+(?:\s+\w+)*)\s+(Wi-Fi|WiFi|LTE)\s*[-–]\s*([\d.,]+)',
            'groups': ['generation', 'chip', 'storage', 'color', 'connectivity', 'price'],
            'variant': 'Pro'
        },
        # 20. iPad 11 256GB Pink Wi-Fi (2025) 36500
        {
            'pattern': r'iPad\s+(\d+)\s+(\d+GB?)\s+(\w+(?:\s+\w+)*)\s+(Wi-Fi|WiFi|LTE)\s*\([^)]+\)\s+(\d+)',
            'groups': ['generation', 'storage', 'color', 'connectivity', 'price'],
            'variant': ''
        },
        # 21. iPad Air 4 64GB Gray WIFI 2020 30200
        {
            'pattern': r'iPad\s+Air\s+(\d+)\s+(\d+GB?)\s+(\w+(?:\s+\w+)*)\s+(Wi-Fi|WiFi|LTE)\s+(\d{4})\s+(\d+)',
            'groups': ['generation', 'storage', 'color', 'connectivity', 'year', 'price'],
            'variant': 'Air'
        },
        # 22. iPad Air 11 128GB Starlight LTE (2025) M3 59000
        {
            'pattern': r'iPad\s+Air\s+(\d+)\s+(\d+GB?)\s+(\w+(?:\s+\w+)*)\s+(LTE|Wi-Fi|WiFi)\s*\([^)]+\)\s+(M\d+)\s+(\d+)',
            'groups': ['generation', 'storage', 'color', 'connectivity', 'chip', 'price'],
            'variant': 'Air'
        },
        # 23. iPad Pro 11 128GB Silver WIFI (2021) 47000
        {
            'pattern': r'iPad\s+Pro\s+(\d+)\s+(\d+GB?)\s+(\w+(?:\s+\w+)*)\s+(Wi-Fi|WiFi|LTE)\s*\([^)]+\)\s+(\d+)',
            'groups': ['generation', 'storage', 'color', 'connectivity', 'price'],
            'variant': 'Pro'
        },
        # 24. iPad Pro 13 1TB Space Black LTE (2024) M4 137000
        {
            'pattern': r'iPad\s+Pro\s+(\d+)\s+(\d+TB?)\s+(\w+(?:\s+\w+)*)\s+(LTE|Wi-Fi|WiFi)\s*\([^)]+\)\s+(M\d+)\s+(\d+)',
            'groups': ['generation', 'storage', 'color', 'connectivity', 'chip', 'price'],
            'variant': 'Pro'
        },
        # 25. iPad Mini 7 256 Blue Wi-Fi 43500🇺🇸
        {
            'pattern': r'iPad\s+Mini\s+(\d+)\s+(\d+)\s+(\w+(?:\s+\w+)*)\s+(Wi-Fi|WiFi|LTE)\s+(\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]*)',
            'groups': ['generation', 'storage', 'color', 'connectivity', 'price', 'country'],
            'variant': 'Mini'
        },
        # 26. iPad 10 256 Blue Wi-Fi 31000🇺🇸
        {
            'pattern': r'iPad\s+(\d+)\s+(\d+)\s+(\w+(?:\s+\w+)*)\s+(Wi-Fi|WiFi|LTE)\s+(\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]*)',
            'groups': ['generation', 'storage', 'color', 'connectivity', 'price', 'country'],
            'variant': ''
        },
        # 27. iPad 11 128 Blue Wi-Fi 31200🇺🇸
        {
            'pattern': r'iPad\s+(\d+)\s+(\d+)\s+(\w+(?:\s+\w+)*)\s+(Wi-Fi|WiFi|LTE)\s+(\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]*)',
            'groups': ['generation', 'storage', 'color', 'connectivity', 'price', 'country'],
            'variant': ''
        },
        # 28. iPad Air 11 M3 (2025) 128 Wi-Fi Space Gray 45500🇺🇸
        {
            'pattern': r'iPad\s+Air\s+(\d+)\s+(M\d+)\s*\([^)]+\)\s+(\d+)\s+(Wi-Fi|WiFi|LTE)\s+(\w+(?:\s+\w+)*)\s+(\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]*)',
            'groups': ['generation', 'chip', 'storage', 'connectivity', 'color', 'price', 'country'],
            'variant': 'Air'
        },
        # 29. iPad Pro 11 512 M4 Space Black LTE 112000🇺🇸
        {
            'pattern': r'iPad\s+Pro\s+(\d+)\s+(\d+)\s+(M\d+)\s+(\w+(?:\s+\w+)*)\s+(LTE|Wi-Fi|WiFi)\s+(\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]*)',
            'groups': ['generation', 'storage', 'chip', 'color', 'connectivity', 'price', 'country'],
            'variant': 'Pro'
        },
        # 30. IPad 11 256 Yellow WIFI MD4J4 - 36.000
        {
            'pattern': r'IPad\s+(\d+)\s+(\d+)\s+(\w+(?:\s+\w+)*)\s+(Wi-Fi|WiFi|LTE)\s+([A-Z0-9]+)\s*[-–]\s*([\d.,]+)',
            'groups': ['generation', 'storage', 'color', 'connectivity', 'product_code', 'price'],
            'variant': ''
        },
        # 31. iPad Air 11 2024 1TB Starlight Wi-Fi - 81.000
        {
            'pattern': r'iPad\s+Air\s+(\d+)\s+(\d{4})\s+(\d+TB?)\s+(\w+(?:\s+\w+)*)\s+(Wi-Fi|WiFi|LTE)\s*[-–]\s*([\d.,]+)',
            'groups': ['generation', 'year', 'storage', 'color', 'connectivity', 'price'],
            'variant': 'Air'
        },
        # 32. iPad Air 13 2024 256 LTE Purple - 76.000
        {
            'pattern': r'iPad\s+Air\s+(\d+)\s+(\d{4})\s+(\d+)\s+(LTE|Wi-Fi|WiFi)\s+(\w+(?:\s+\w+)*)\s*[-–]\s*([\d.,]+)',
            'groups': ['generation', 'year', 'storage', 'connectivity', 'color', 'price'],
            'variant': 'Air'
        },
        # 33. iPad Pro 11 M4 1TB Black Wi-Fi - 136.000
        {
            'pattern': r'iPad\s+Pro\s+(\d+)\s+(M\d+)\s+(\d+TB?)\s+(\w+(?:\s+\w+)*)\s+(Wi-Fi|WiFi|LTE)\s*[-–]\s*([\d.,]+)',
            'groups': ['generation', 'chip', 'storage', 'color', 'connectivity', 'price'],
            'variant': 'Pro'
        },
        # 34. iPad Pro 13 M4 1TB Black LTE - 146.000
        {
            'pattern': r'iPad\s+Pro\s+(\d+)\s+(M\d+)\s+(\d+TB?)\s+(\w+(?:\s+\w+)*)\s+(LTE|Wi-Fi|WiFi)\s*[-–]\s*([\d.,]+)',
            'groups': ['generation', 'chip', 'storage', 'color', 'connectivity', 'price'],
            'variant': 'Pro'
        },
        # 35. iPad Pro 13 M4 2TB Silver LTE - 156.000
        {
            'pattern': r'iPad\s+Pro\s+(\d+)\s+(M\d+)\s+(\d+TB?)\s+(\w+(?:\s+\w+)*)\s+(LTE|Wi-Fi|WiFi)\s*[-–]\s*([\d.,]+)',
            'groups': ['generation', 'chip', 'storage', 'color', 'connectivity', 'price'],
            'variant': 'Pro'
        },
        # 36. iPad 11 256 Yellow Wi-Fi🇺🇸 36200 (без пробела перед флагом)
        {
            'pattern': r'iPad\s+(\d+)\s+(\d+)\s+(\w+(?:\s+\w+)*)\s+(Wi-Fi|WiFi|LTE)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]+)\s+(\d+)',
            'groups': ['generation', 'storage', 'color', 'connectivity', 'country', 'price'],
            'variant': ''
        },
        # 37. iPad Mini 7 256GB Strarlight Wi-Fi MXND3 42800 (с опечаткой)
        {
            'pattern': r'iPad\s+Mini\s+(\d+)\s+(\d+GB?)\s+(\w+(?:\s+\w+)*)\s+(Wi-Fi|WiFi|LTE)\s+([A-Z0-9]+)\s+(\d+)',
            'groups': ['generation', 'storage', 'color', 'connectivity', 'product_code', 'price'],
            'variant': 'Mini'
        }
        ]
        
        # Маппинг подключений
        self.connectivity_map = {
            'Wi-Fi': 'Wi-Fi',
            'WiFi': 'Wi-Fi', 
            'LTE': 'LTE',
            'wifi': 'Wi-Fi',
            'wi-fi': 'Wi-Fi',
            'lte': 'LTE'
        }

    def parse_lines(self, lines: List[str]) -> Tuple[List[iPadData], List[str]]:
        """Парсит список строк"""
        parsed_items = []
        unparsed_lines = []
        
        for line in lines:
            result = self._parse_single_line(line)
            if result:
                parsed_items.append(result)
            else:
                unparsed_lines.append(line)
        
        return parsed_items, unparsed_lines

    def _parse_single_line(self, line: str) -> Optional[iPadData]:
        """Парсит одну строку"""
        line_lower = line.lower()
        
        # Проверяем, что это iPad
        if 'ipad' not in line_lower and 'mini' not in line_lower:
            return None
        
        # Пробуем разные паттерны
        for i, pattern_info in enumerate(self.patterns):
            match = re.search(pattern_info['pattern'], line, re.IGNORECASE)
            if match:
                return self._extract_data_from_match(match, pattern_info, line, i)
        
        return None

    def _extract_data_from_match(self, match, pattern_info: Dict, line: str, pattern_index: int) -> iPadData:
        """Извлекает данные из regex match"""
        groups = match.groups()
        data = {}
        
        # Извлекаем данные по группам
        for i, group_name in enumerate(pattern_info['groups']):
            if i < len(groups):
                data[group_name] = groups[i]
        
        # Нормализуем данные
        generation = data.get('generation', '')
        variant = pattern_info.get('variant', '')
        storage = self._normalize_storage(data.get('storage', ''))
        color = self._normalize_color(data.get('color', ''))
        connectivity = self.connectivity_map.get(data.get('connectivity', ''), data.get('connectivity', ''))
        country = data.get('country', '')
        price = self._parse_price(data.get('price', '0'))
        
        # Определяем размер
        size = generation
        
        # Обрабатываем специальные случаи
        if pattern_index == 17:  # iPad Mini 2024 128 Black LTE - 53.000
            # Для этого паттерна generation = year, нужно поменять местами
            year = data.get('year', '')
            if year:
                generation = f"Mini {year}"
                size = year
        elif pattern_index == 21:  # iPad Air 4 64GB Gray WIFI 2020 30200
            # Для этого паттерна year в конце
            year = data.get('year', '')
            if year:
                generation += f" ({year})"
        elif pattern_index == 22:  # iPad Air 11 128GB Starlight LTE (2025) M3 59000
            # Для этого паттерна chip в конце
            chip = data.get('chip', '')
            if chip:
                generation += f" {chip}"
        elif pattern_index == 24:  # iPad Pro 13 1TB Space Black LTE (2024) M4 137000
            # Для этого паттерна chip в конце
            chip = data.get('chip', '')
            if chip:
                generation += f" {chip}"
        elif pattern_index == 28:  # iPad Air 11 M3 (2025) 128 Wi-Fi Space Gray 45500🇺🇸
            # Для этого паттерна chip в начале
            chip = data.get('chip', '')
            if chip:
                generation += f" {chip}"
        elif pattern_index == 29:  # iPad Pro 11 512 M4 Space Black LTE 112000🇺🇸
            # Для этого паттерна chip в середине
            chip = data.get('chip', '')
            if chip:
                generation += f" {chip}"
        elif pattern_index == 31:  # iPad Air 11 2024 1TB Starlight Wi-Fi - 81.000
            # Для этого паттерна year в середине
            year = data.get('year', '')
            if year:
                generation += f" ({year})"
        elif pattern_index == 32:  # iPad Air 13 2024 256 LTE Purple - 76.000
            # Для этого паттерна year в середине
            year = data.get('year', '')
            if year:
                generation += f" ({year})"
        
        # Формируем полное поколение
        if variant:
            generation = f"{variant} {generation}"
        
        # Добавляем чип если есть
        chip = data.get('chip', '')
        if chip:
            generation += f" {chip}"
        
        # Добавляем год если есть (для паттернов с годом)
        year = data.get('year', '')
        if year and pattern_index != 17:  # Не для паттерна 17, там год уже обработан
            generation += f" ({year})"
        
        return iPadData(
            generation=generation,
            variant=variant,
            size=size,
            storage=storage,
            color=color,
            connectivity=connectivity,
            product_code='',
            country=country,
            price=price,
            source_line=line
        )

    def _normalize_storage(self, storage: str) -> str:
        """Нормализует объем памяти"""
        if not storage:
            return ""
        
        # Убираем лишние пробелы
        storage = storage.strip()
        
        # Добавляем GB если нет
        if storage.isdigit():
            storage = f"{storage}GB"
        elif not storage.upper().endswith('GB') and not storage.upper().endswith('TB'):
            storage = f"{storage}GB"
        
        return storage

    def _normalize_color(self, color: str) -> str:
        """Нормализует цвет"""
        if not color:
            return ""
        
        # Убираем лишние пробелы и приводим к правильному регистру
        color = color.strip().title()
        
        return color

    def _parse_price(self, price_str: str) -> int:
        """Парсит цену"""
        if not price_str:
            return 0
        
        # Убираем все кроме цифр, точек и запятых
        price_str = re.sub(r'[^\d.,]', '', str(price_str))
        
        if not price_str:
            return 0
        
        # Обрабатываем точку как разделитель тысяч
        if '.' in price_str and ',' not in price_str:
            # Если есть точка, но нет запятой, то точка - разделитель тысяч
            price_str = price_str.replace('.', '')
        elif ',' in price_str:
            # Если есть запятая, то она - разделитель тысяч
            price_str = price_str.replace(',', '')
        
        try:
            return int(price_str)
        except ValueError:
            return 0
