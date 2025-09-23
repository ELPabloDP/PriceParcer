"""
Парсер для Apple Watch
"""
import re
import logging
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class AppleWatchData:
    """Структура данных для цены Apple Watch"""
    model: str  # SE, S10, Ultra
    generation: str  # 2, 2024, Ultra 2
    size: str   # 40, 44, 46, 49
    color: str  # Midnight, Silver, etc.
    band_type: str  # Sport Band, Sport Loop, etc.
    band_size: str  # S/M, M/L
    connectivity: str  # GPS, LTE
    country_flag: str  # 🇺🇸, 🇯🇵, etc.
    price: int
    product_code: str = ""
    source_line: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Конвертирует в словарь для сохранения"""
        return {
            'firm': 'Apple',
            'device': 'Apple Watch',
            'generation': self.generation,
            'variant': f"{self.model} {self.size}mm",
            'size': f"{self.size}mm",
            'color': self.color,
            'band_type': self.band_type,
            'band_size': self.band_size,
            'connectivity': self.connectivity,
            'configuration': f"{self.color} {self.band_type} {self.band_size}",
            'product_code': self.product_code,
            'country': self.country_flag,
            'price': self.price
        }

class AppleWatchParser:
    """Парсер для Apple Watch"""
    
    def __init__(self):
        self.patterns = [
            # SE 2024 40mm Silver S/M - 16000
            r'SE\s+(\d{4})\s+(\d{2})mm\s+([A-Za-z\s]+?)\s+([SM]/[ML])\s*-\s*(\d+[.,]\d+|\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]*)',
            
            # SE 2024 40mm Silver M/L - 16000
            r'SE\s+(\d{4})\s+(\d{2})mm\s+([A-Za-z\s]+?)\s+([ML]/[LM])\s*-\s*(\d+[.,]\d+|\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]*)',
            
            # 10 46mm Rose Gold M/L - 29000
            r'(\d{1,2})\s+(\d{2})mm\s+([A-Za-z\s]+?)\s+([SM]/[ML]|[ML]/[LM])\s*-\s*(\d+[.,]\d+|\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇤🇷🇪🇺🇷🇺🇨🇦🇻🇳]*)',
            
            # Ultra 2 49mm Black Trail Loop M/L - 60000
            r'Ultra\s+(\d+)\s+(\d{2})mm\s+([A-Za-z\s]+?)\s+([A-Za-z\s]+?)\s+([SM]/[ML]|[ML]/[LM])\s*-\s*(\d+[.,]\d+|\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇤🇷🇪🇺🇷🇺🇨🇦🇻🇳]*)',
            
            # Ultra 2 49mm Black Ti Dark Green Alpine Loop M - 59500
            r'Ultra\s+(\d+)\s+(\d{2})mm\s+([A-Za-z\s]+?)\s+Ti\s+([A-Za-z\s]+?)\s+([A-Za-z\s]+?)\s+([SML])\s*-\s*(\d+[.,]\d+|\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇤🇷🇪🇺🇷🇺🇨🇦🇻🇳]*)',
            
            # Apple Watch SE 40 Midnight S/M 2024 16300
            r'Apple\s+Watch\s+SE\s+(\d{2})\s+([A-Za-z\s]+?)\s+([SM]/[ML]|[ML]/[LM])\s+(\d{4})\s+(\d+[.,]\d+|\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇤🇷🇪🇺🇷🇺🇨🇦🇻🇳]*)',
            
            # Apple Watch S10 42 Rose Gold Al LB S/M GPS MWWH3 28000
            r'Apple\s+Watch\s+S(\d{1,2})\s+(\d{2})\s+([A-Za-z\s]+?)\s+Al\s+([A-Za-z\s]*?)\s+([SM]/[ML]|[ML]/[LM])\s+GPS\s+([A-Z0-9]+)\s+(\d+[.,]\d+|\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇤🇷🇪🇺🇷🇺🇨🇦🇻🇳]*)',
            
            # Apple Watch Ultra 2 49 Blue\Black (S\M) 56200
            r'Apple\s+Watch\s+Ultra\s+(\d+)\s+(\d{2})\s+([A-Za-z\\]+?)\s*\(([SM]\\[ML]|[ML]\\[LM])\)\s+(\d+[.,]\d+|\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇤🇷🇪🇺🇷🇺🇨🇦🇻🇳]*)',
            
            # AW SE 2024 40mm Midnight SB Midnight S/M - 16500
            r'AW\s+SE\s+(\d{4})\s+(\d{2})mm\s+([A-Za-z\s]+?)\s+SB\s+([A-Za-z\s]+?)\s+([SM]/[ML]|[ML]/[LM])\s*-\s*(\d+[.,]\d+|\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇤🇷🇪🇺🇷🇺🇨🇦🇻🇳]*)',
            
            # AW 10 46 Rose Gold M/L 29900🇺🇸
            r'AW\s+(\d{1,2})\s+(\d{2})\s+([A-Za-z\s]+?)\s+([SM]/[ML]|[ML]/[LM])\s+(\d+[.,]\d+|\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇤🇷🇪🇺🇷🇺🇨🇦🇻🇳]+)',
            
            # S10 42 Rose Gold - 28500🇺🇸
            r'S(\d{1,2})\s+(\d{2})\s+([A-Za-z\s]+?)\s*-\s*(\d+[.,]\d+|\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇤🇷🇪🇺🇷🇺🇨🇦🇻🇳]+)',
            
            # SE2 40 Midnight - 16300🇺🇸
            r'SE(\d+)\s+(\d{2})\s+([A-Za-z\s]+?)\s*-\s*(\d+[.,]\d+|\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇤🇷🇪🇺🇷🇺🇨🇦🇻🇳]+)',
        ]
        
        # Цвета Apple Watch
        self.colors = {
            'midnight': 'Midnight',
            'silver': 'Silver',
            'starlight': 'Starlight',
            'gold': 'Gold',
            'rose gold': 'Rose Gold',
            'jet black': 'Jet Black',
            'black': 'Black',
            'natural': 'Natural',
            'blue': 'Blue',
            'green': 'Green',
            'pink': 'Pink',
            'red': 'Red',
            'purple': 'Purple',
            'orange': 'Orange'
        }
        
        # Типы ремешков
        self.band_types = {
            'sb': 'Sport Band',
            'sl': 'Sport Loop',
            'trail loop': 'Trail Loop',
            'alpine loop': 'Alpine Loop',
            'ocean band': 'Ocean Band',
            'milanese loop': 'Milanese Loop',
            'sport band': 'Sport Band',
            'sport loop': 'Sport Loop'
        }

    def parse_lines(self, lines: List[str]) -> Tuple[List[AppleWatchData], List[str]]:
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
                logger.warning(f"Ошибка парсинга строки Apple Watch: {line} - {e}")
                unparsed_lines.append(line)
        
        return parsed_data, unparsed_lines

    def _parse_single_line(self, line: str) -> AppleWatchData:
        """Парсит одну строку Apple Watch"""
        for i, pattern in enumerate(self.patterns):
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                groups = match.groups()
                logger.info(f"Apple Watch паттерн {i} сработал для строки: {line}, групп: {len(groups)}")
                
                try:
                    if i == 0 or i == 1:  # SE 2024 40mm Silver S/M - 16000
                        year, size, color, band_size, price, country = groups
                        model = 'SE'
                        generation = year
                        band_type = 'Sport Band'
                        connectivity = 'GPS'
                        
                    elif i == 2:  # 10 46mm Rose Gold M/L - 29000
                        series, size, color, band_size, price, country = groups
                        model = f'S{series}'
                        generation = series
                        band_type = 'Sport Band'
                        connectivity = 'GPS'
                        
                    elif i == 3:  # Ultra 2 49mm Black Trail Loop M/L - 60000
                        gen, size, color, band_type_raw, band_size, price, country = groups
                        model = 'Ultra'
                        generation = f'Ultra {gen}'
                        band_type = self._normalize_band_type(band_type_raw)
                        connectivity = 'GPS'
                        
                    elif i == 4:  # Ultra 2 49mm Black Ti Dark Green Alpine Loop M - 59500
                        gen, size, color_base, color_accent, band_type_raw, band_size_single, price, country = groups
                        model = 'Ultra'
                        generation = f'Ultra {gen}'
                        color = f"{color_base} Ti {color_accent}"
                        band_type = self._normalize_band_type(band_type_raw)
                        band_size = f"{band_size_single}"
                        connectivity = 'GPS'
                        
                    elif i == 5:  # Apple Watch SE 40 Midnight S/M 2024 16300
                        size, color, band_size, year, price, country = groups
                        model = 'SE'
                        generation = year
                        band_type = 'Sport Band'
                        connectivity = 'GPS'
                        
                    elif i == 6:  # Apple Watch S10 42 Rose Gold Al LB S/M GPS MWWH3 28000
                        series, size, color, band_type_raw, band_size, product_code, price, country = groups
                        model = f'S{series}'
                        generation = series
                        band_type = self._normalize_band_type(band_type_raw) or 'Sport Band'
                        connectivity = 'GPS'
                        
                    elif i == 7:  # Apple Watch Ultra 2 49 Blue\Black (S\M) 56200
                        gen, size, color, band_size, price, country = groups
                        model = 'Ultra'
                        generation = f'Ultra {gen}'
                        band_type = 'Trail Loop'
                        connectivity = 'GPS'
                        band_size = band_size.replace('\\', '/')
                        
                    elif i == 8:  # AW SE 2024 40mm Midnight SB Midnight S/M - 16500
                        year, size, color, band_type_raw, band_color, band_size, price, country = groups
                        model = 'SE'
                        generation = year
                        band_type = self._normalize_band_type(band_type_raw)
                        connectivity = 'GPS'
                        
                    elif i == 9:  # AW 10 46 Rose Gold M/L 29900🇺🇸
                        series, size, color, band_size, price, country = groups
                        model = f'S{series}'
                        generation = series
                        band_type = 'Sport Band'
                        connectivity = 'GPS'
                        
                    elif i == 10:  # S10 42 Rose Gold - 28500🇺🇸
                        series, size, color, price, country = groups
                        model = f'S{series}'
                        generation = series
                        band_type = 'Sport Band'
                        band_size = 'M/L'
                        connectivity = 'GPS'
                        
                    elif i == 11:  # SE2 40 Midnight - 16300🇺🇸
                        gen, size, color, price, country = groups
                        model = 'SE'
                        generation = f'SE{gen}'
                        band_type = 'Sport Band'
                        band_size = 'M/L'
                        connectivity = 'GPS'
                    
                    # Нормализуем данные
                    color = self._normalize_color(color)
                    price = int(price.replace('.', '').replace(',', ''))
                    
                    return AppleWatchData(
                        model=model,
                        generation=generation,
                        size=size,
                        color=color,
                        band_type=band_type,
                        band_size=band_size,
                        connectivity=connectivity,
                        country_flag=country,
                        price=price,
                        product_code=getattr(self, 'product_code', ''),
                        source_line=line
                    )
                    
                except Exception as e:
                    logger.error(f"Ошибка парсинга Apple Watch группы {i}: {e}")
                    continue
        
        return None

    def _normalize_color(self, color: str) -> str:
        """Нормализует цвет"""
        color_lower = color.lower().strip()
        return self.colors.get(color_lower, color.title())

    def _normalize_band_type(self, band_type: str) -> str:
        """Нормализует тип ремешка"""
        if not band_type:
            return 'Sport Band'
        band_lower = band_type.lower().strip()
        return self.band_types.get(band_lower, band_type.title())

    def _is_apple_watch_line(self, line: str) -> bool:
        """Проверяет, является ли строка описанием Apple Watch"""
        line_lower = line.lower()
        
        # Проверяем наличие ключевых слов
        has_watch = 'watch' in line_lower or 'se' in line_lower or 'ultra' in line_lower
        has_size = bool(re.search(r'\d{2}mm|\d{2}\s', line))
        has_price = bool(re.search(r'\d{4,6}|\d+[.,]\d+', line))
        
        return has_watch and has_size and has_price