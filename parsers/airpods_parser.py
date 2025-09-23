"""
Парсер для AirPods
"""
import re
import logging
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class AirPodsData:
    """Структура данных для цены AirPods"""
    model: str  # AirPods, AirPods Pro, AirPods Max
    generation: str  # 2, 3, 4, Pro, Pro 2, Max
    features: str  # ANC, Lightning, USB-C
    color: str  # White, Purple, Orange, etc.
    year: str   # 2024, NEW, etc.
    country_flag: str  # 🇺🇸, 🇯🇵, etc.
    price: int
    product_code: str = ""
    source_line: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Конвертирует в словарь для сохранения"""
        return {
            'firm': 'Apple',
            'device': 'AirPods',
            'generation': self.generation,
            'variant': self.model,
            'features': self.features,
            'color': self.color,
            'year': self.year,
            'configuration': f"{self.model} {self.features} {self.color}",
            'product_code': self.product_code,
            'country': self.country_flag,
            'price': self.price
        }

class AirPodsParser:
    """Парсер для AirPods"""
    
    def __init__(self):
        self.patterns = [
            # 🎧AirPods 4 - 9000🇪🇺
            r'🎧AirPods\s+(\d+)\s*-\s*(\d+[.,]\d+|\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇤🇷🇪🇺🇷🇺🇨🇦🇻🇳]*)',
            
            # 🎧AirPods 4 ANC - 12900🇪🇺
            r'🎧AirPods\s+(\d+)\s+(ANC|ANС)\s*-\s*(\d+[.,]\d+|\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇤🇷🇪🇺🇷🇺🇨🇦🇻🇳]*)',
            
            # 🎧AirPods Pro NEW - 15200🇪🇺
            r'🎧AirPods\s+Pro\s+(NEW|new)\s*-\s*(\d+[.,]\d+|\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇤🇷🇪🇺🇷🇺🇨🇦🇻🇳]*)',
            
            # AirPods Max 2024 Orange - 40000🇺🇸
            r'AirPods\s+Max\s+(\d{4})\s+([A-Za-z\s]+?)\s*-\s*(\d+[.,]\d+|\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇤🇷🇪🇺🇷🇺🇨🇦🇻🇳]*)',
            
            # AirPods Max Blue Lightning - 35500
            r'AirPods\s+Max\s+([A-Za-z\s]+?)\s+(Lightning|USB-C)\s*-\s*(\d+[.,]\d+|\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇤🇷🇪🇺🇷🇺🇨🇦🇻🇳]*)',
            
            # AirPods 4 - 9000
            r'AirPods\s+(\d+)\s*-\s*(\d+[.,]\d+|\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇤🇷🇪🇺🇷🇺🇨🇦🇻🇳]*)',
            
            # AirPods 3 Lightning 8400
            r'AirPods\s+(\d+)\s+(Lightning|USB-C)\s+(\d+[.,]\d+|\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇤🇷🇪🇺🇷🇺🇨🇦🇻🇳]*)',
            
            # AirPods 4 ANC 12700
            r'AirPods\s+(\d+)\s+(ANC|ANС)\s+(\d+[.,]\d+|\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇤🇷🇪🇺🇷🇺🇨🇦🇻🇳]*)',
            
            # Airpods Max Purple 2024 USB-CMWW83 38800
            r'Airpods\s+Max\s+([A-Za-z\s]+?)\s+(\d{4})\s+(USB-C|Lightning)([A-Z0-9]*)\s+(\d+[.,]\d+|\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇤🇷🇪🇺🇷🇺🇨🇦🇻🇳]*)',
            
            # Apple AirPods 3 8400 🇺🇸
            r'Apple\s+AirPods\s+(\d+)\s+(\d+[.,]\d+|\d+)\s+([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇤🇷🇪🇺🇷🇺🇨🇦🇻🇳]+)',
            
            # Apple AirPods 4 ANC 12700 🇺🇸
            r'Apple\s+AirPods\s+(\d+)\s+(ANC|ANС)\s+(\d+[.,]\d+|\d+)\s+([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇤🇷🇪🇺🇷🇺🇨🇦🇻🇳]+)',
            
            # Apple AirPods MAX Orange 2024 38300 🇺🇸
            r'Apple\s+AirPods\s+MAX\s+([A-Za-z\s]+?)\s+(\d{4})\s+(\d+[.,]\d+|\d+)\s+([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇤🇷🇪🇺🇷🇺🇨🇦🇻🇳]+)',
            
            # Apple AirPods Pro 2 New 2023 15000 🇺🇸
            r'Apple\s+AirPods\s+Pro\s+(\d+)\s+(New|NEW)\s+(\d{4})\s+(\d+[.,]\d+|\d+)\s+([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇤🇷🇪🇺🇷🇺🇨🇦🇻🇳]+)',
            
            # Airpods 3 Lightning MPNY3 - 8.400
            r'Airpods\s+(\d+)\s+(Lightning|USB-C)\s+([A-Z0-9]+)\s*-\s*(\d+[.,]\d+|\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇤🇷🇪🇺🇷🇺🇨🇦🇻🇳]*)',
            
            # Airpods Max Purple 2024 USB- 39.000
            r'Airpods\s+Max\s+([A-Za-z\s]+?)\s+(\d{4})\s+(USB|Lightning)[-C]*\s*-?\s*(\d+[.,]\d+|\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇤🇷🇪🇺🇷🇺🇨🇦🇻🇳]*)',
        ]
        
        # Цвета AirPods
        self.colors = {
            'white': 'White',
            'purple': 'Purple',
            'orange': 'Orange',
            'blue': 'Blue',
            'pink': 'Pink',
            'green': 'Green',
            'black': 'Black',
            'silver': 'Silver',
            'gold': 'Gold'
        }

    def parse_lines(self, lines: List[str]) -> Tuple[List[AirPodsData], List[str]]:
        """Парсит список строк и возвращает распознанные данные"""
        parsed_data = []
        unparsed_lines = []
        
        for line in lines:
            try:
                result = self._parse_single_line(line)
                if result:
                    parsed_data.append(result)
                else:
                    unparsed_lines.append(line)
            except Exception as e:
                logger.warning(f"Ошибка парсинга строки AirPods: {line} - {e}")
                unparsed_lines.append(line)
        
        return parsed_data, unparsed_lines

    def _parse_single_line(self, line: str) -> AirPodsData:
        """Парсит одну строку AirPods"""
        for i, pattern in enumerate(self.patterns):
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                groups = match.groups()
                logger.info(f"AirPods паттерн {i} сработал для строки: {line}, групп: {len(groups)}")
                
                try:
                    if i == 0:  # 🎧AirPods 4 - 9000🇪🇺
                        generation, price, country = groups
                        model = 'AirPods'
                        features = ''
                        color = 'White'
                        year = ''
                        product_code = ''
                        
                    elif i == 1:  # 🎧AirPods 4 ANC - 12900🇪🇺
                        generation, anc, price, country = groups
                        model = 'AirPods'
                        features = 'ANC'
                        color = 'White'
                        year = ''
                        product_code = ''
                        
                    elif i == 2:  # 🎧AirPods Pro NEW - 15200🇪🇺
                        new_flag, price, country = groups
                        model = 'AirPods Pro'
                        generation = 'Pro'
                        features = 'NEW'
                        color = 'White'
                        year = ''
                        product_code = ''
                        
                    elif i == 3:  # AirPods Max 2024 Orange - 40000🇺🇸
                        year, color, price, country = groups
                        model = 'AirPods Max'
                        generation = 'Max'
                        features = ''
                        product_code = ''
                        
                    elif i == 4:  # AirPods Max Blue Lightning - 35500
                        color, connector, price, country = groups
                        model = 'AirPods Max'
                        generation = 'Max'
                        features = connector
                        year = ''
                        product_code = ''
                        
                    elif i == 5:  # AirPods 4 - 9000
                        generation, price, country = groups
                        model = 'AirPods'
                        features = ''
                        color = 'White'
                        year = ''
                        product_code = ''
                        
                    elif i == 6:  # AirPods 3 Lightning 8400
                        generation, connector, price, country = groups
                        model = 'AirPods'
                        features = connector
                        color = 'White'
                        year = ''
                        product_code = ''
                        
                    elif i == 7:  # AirPods 4 ANC 12700
                        generation, anc, price, country = groups
                        model = 'AirPods'
                        features = 'ANC'
                        color = 'White'
                        year = ''
                        product_code = ''
                        
                    elif i == 8:  # Airpods Max Purple 2024 USB-CMWW83 38800
                        color, year, connector, product_code, price, country = groups
                        model = 'AirPods Max'
                        generation = 'Max'
                        features = connector
                        
                    elif i == 9:  # Apple AirPods 3 8400 🇺🇸
                        generation, price, country = groups
                        model = 'AirPods'
                        features = ''
                        color = 'White'
                        year = ''
                        product_code = ''
                        
                    elif i == 10:  # Apple AirPods 4 ANC 12700 🇺🇸
                        generation, anc, price, country = groups
                        model = 'AirPods'
                        features = 'ANC'
                        color = 'White'
                        year = ''
                        product_code = ''
                        
                    elif i == 11:  # Apple AirPods MAX Orange 2024 38300 🇺🇸
                        color, year, price, country = groups
                        model = 'AirPods Max'
                        generation = 'Max'
                        features = ''
                        product_code = ''
                        
                    elif i == 12:  # Apple AirPods Pro 2 New 2023 15000 🇺🇸
                        pro_gen, new_flag, year, price, country = groups
                        model = 'AirPods Pro'
                        generation = f'Pro {pro_gen}'
                        features = 'NEW'
                        color = 'White'
                        product_code = ''
                        
                    elif i == 13:  # Airpods 3 Lightning MPNY3 - 8.400
                        generation, connector, product_code, price, country = groups
                        model = 'AirPods'
                        features = connector
                        color = 'White'
                        year = ''
                        
                    elif i == 14:  # Airpods Max Purple 2024 USB- 39.000
                        color, year, connector, price, country = groups
                        model = 'AirPods Max'
                        generation = 'Max'
                        features = connector
                        product_code = ''
                    
                    # Нормализуем данные
                    color = self._normalize_color(color)
                    price = int(price.replace('.', '').replace(',', ''))
                    
                    return AirPodsData(
                        model=model,
                        generation=generation,
                        features=features,
                        color=color,
                        year=year,
                        country_flag=country,
                        price=price,
                        product_code=product_code,
                        source_line=line
                    )
                    
                except Exception as e:
                    logger.error(f"Ошибка парсинга AirPods группы {i}: {e}")
                    continue
        
        return None

    def _normalize_color(self, color: str) -> str:
        """Нормализует цвет"""
        color_lower = color.lower().strip()
        return self.colors.get(color_lower, color.title())

    def _is_airpods_line(self, line: str) -> bool:
        """Проверяет, является ли строка описанием AirPods"""
        line_lower = line.lower()
        
        # Проверяем наличие ключевых слов
        has_airpods = 'airpods' in line_lower or '🎧' in line
        has_price = bool(re.search(r'\d{4,6}|\d+[.,]\d+', line))
        
        return has_airpods and has_price
