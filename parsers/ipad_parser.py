"""
Парсер для iPad
"""
import re
from typing import List, Dict, Any, Tuple
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
    """Парсер для iPad"""
    
    def __init__(self):
        # Паттерны для разных типов iPad
        self.patterns = [
            # iPad 11 256 Yellow WIFI MD4J4 - 36.000
            r'ipad\s+(\d+)\s+(\d+)\s+(\w+)\s+(wifi|lte|wi-fi)\s+([a-z0-9]+)\s*[-–]\s*([\d.,]+)',
            
            # iPad Mini 7 256 Starlight WiFi- 43000🇺🇸
            r'ipad\s+mini\s+(\d+)\s+(\d+gb)\s+(\w+)\s+(wifi|lte)[-–]\s*([\d.,]+)([🇺🇸🇯🇵🇮🇳🇪🇺🇦🇪🇨🇦🇻🇳]*)',
            
            # iPad Air 11 M3 128 Blue Wi-Fi 🇺🇸 42500
            r'ipad\s+air\s+(\d+)\s+(m\d+)\s+(\d+gb)\s+(\w+)\s+(wi-fi|wifi|lte)\s*([🇺🇸🇯🇵🇮🇳🇪🇺🇦🇪🇨🇦🇻🇳]*)\s*([\d.,]+)',
            
            # iPad Pro 11 M4 256 Black LTE - 95.000
            r'ipad\s+pro\s+(\d+)\s+(m\d+)\s+(\d+gb)\s+(\w+)\s+(lte|wi-fi|wifi)[-–]\s*([\d.,]+)',
            
            # iPad 9 64GB Gray LTE 24500
            r'ipad\s+(\d+)\s+(\d+gb)\s+(\w+)\s+(lte|wifi|wi-fi)\s*([\d.,]+)',
            
            # iPad Air 11 M3 (2025) 128 Blue Wi-Fi 🇺🇸 42500
            r'ipad\s+air\s+(\d+)\s+(m\d+)\s*\([^)]+\)\s+(\d+gb)\s+(\w+)\s+(wi-fi|wifi|lte)\s*([🇺🇸🇯🇵🇮🇳🇪🇺🇦🇪🇨🇦🇻🇳]*)\s*([\d.,]+)',
            
            # iPad Pro 13 M4 1TB Black LTE - 146.000
            r'ipad\s+pro\s+(\d+)\s+(m\d+)\s+(\d+gb)\s+(\w+)\s+(lte|wi-fi|wifi)[-–]\s*([\d.,]+)',
            
            # iPad 11 256 Yellow WIFI MD4J4 - 36.000 (исправленный паттерн)
            r'ipad\s+(\d+)\s+(\d+gb)\s+(\w+)\s+(wifi|lte)\s+([a-z0-9]+)\s*[-–]\s*([\d.,]+)',
        ]
        
        # Цвета iPad
        self.colors = {
            'gray': 'Space Gray',
            'silver': 'Silver',
            'pink': 'Pink',
            'blue': 'Blue',
            'purple': 'Purple',
            'yellow': 'Yellow',
            'starlight': 'Starlight',
            'black': 'Space Black',
            'white': 'White',
            'gold': 'Gold',
            'rose': 'Rose Gold',
            'green': 'Green',
            'red': 'Red'
        }
        
        # Подключение
        self.connectivity_map = {
            'wifi': 'Wi-Fi',
            'wi-fi': 'Wi-Fi',
            'lte': 'LTE'
        }

    def parse_lines(self, lines: List[str]) -> Tuple[List[iPadData], List[str]]:
        """Парсит строки с iPad"""
        parsed_data = []
        unparsed_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            parsed = self._parse_single_line(line)
            if parsed:
                parsed_data.append(parsed)
            else:
                unparsed_lines.append(line)
        
        logger.info(f"iPad парсер: обработано {len(parsed_data)} строк, нераспознано {len(unparsed_lines)}")
        return parsed_data, unparsed_lines

    def _parse_single_line(self, line: str) -> iPadData:
        """Парсит одну строку"""
        line_lower = line.lower()
        
        # Проверяем, что это iPad
        if not line_lower.startswith('ipad'):
            return None
        
        # Пробуем разные паттерны
        for pattern in self.patterns:
            match = re.search(pattern, line_lower, re.IGNORECASE)
            if match:
                return self._extract_data_from_match(match, line)
        
        return None

    def _extract_data_from_match(self, match: re.Match, original_line: str) -> iPadData:
        """Извлекает данные из совпадения"""
        groups = match.groups()
        
        # Базовые данные
        generation = ""
        variant = ""
        size = ""
        storage = ""
        color = ""
        connectivity = ""
        product_code = ""
        country = ""
        price = 0
        
        # Анализируем группы в зависимости от паттерна
        if len(groups) >= 6:
            if 'mini' in original_line.lower():
                # iPad Mini 7 256 Starlight WiFi- 43000🇺🇸
                generation = f"Mini {groups[0]}"
                variant = "Mini"
                size = groups[0]
                storage = groups[1]
                color = self._normalize_color(groups[2])
                connectivity = self.connectivity_map.get(groups[3], groups[3])
                price = self._parse_price(groups[4])
                country = groups[5] if len(groups) > 5 else ""
                
            elif 'air' in original_line.lower():
                # iPad Air 11 M3 128 Blue Wi-Fi 🇺🇸 42500
                generation = groups[1]  # M3
                variant = "Air"
                size = groups[0]  # 11
                storage = groups[2]
                color = self._normalize_color(groups[3])
                connectivity = self.connectivity_map.get(groups[4], groups[4])
                country = groups[5] if len(groups) > 5 else ""
                price = self._parse_price(groups[6]) if len(groups) > 6 else 0
                
            elif 'pro' in original_line.lower():
                # iPad Pro 11 M4 256 Black LTE - 95.000
                generation = groups[1]  # M4
                variant = "Pro"
                size = groups[0]  # 11
                storage = groups[2]
                color = self._normalize_color(groups[3])
                connectivity = self.connectivity_map.get(groups[4], groups[4])
                price = self._parse_price(groups[5])
                
            else:
                # iPad 11 256 Yellow WIFI MD4J4 - 36.000
                generation = groups[0]  # 11
                size = groups[0]
                storage = f"{groups[1]}GB"  # Добавляем GB
                color = self._normalize_color(groups[2])
                connectivity = self.connectivity_map.get(groups[3], groups[3])
                product_code = groups[4] if len(groups) > 4 else ""
                price = self._parse_price(groups[5]) if len(groups) > 5 else 0
        
        return iPadData(
            generation=generation,
            variant=variant,
            size=size,
            storage=storage,
            color=color,
            connectivity=connectivity,
            product_code=product_code,
            country=country,
            price=price,
            source_line=original_line
        )

    def _normalize_color(self, color: str) -> str:
        """Нормализует цвет"""
        color_lower = color.lower()
        return self.colors.get(color_lower, color.title())

    def _parse_price(self, price_str: str) -> int:
        """Парсит цену"""
        try:
            # Убираем все кроме цифр и точек
            price_clean = re.sub(r'[^\d.,]', '', price_str)
            # Заменяем запятую на точку
            price_clean = price_clean.replace(',', '.')
            return int(float(price_clean))
        except:
            return 0

# Создаем экземпляр парсера
ipad_parser = iPadParser()
