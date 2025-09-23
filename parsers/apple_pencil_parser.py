"""
Парсер для Apple Pencil
"""
import re
import logging
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ApplePencilData:
    """Структура данных для цены Apple Pencil"""
    model: str  # Apple Pencil, Pencil
    generation: str  # 1, 2, Pro, USB-C
    connector: str  # Lightning, USB-C, TYPE-C
    country_flag: str  # 🇺🇸, 🇯🇵, etc.
    price: int
    product_code: str = ""
    source_line: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Конвертирует в словарь для сохранения"""
        return {
            'firm': 'Apple',
            'device': 'Apple Pencil',
            'generation': self.generation,
            'variant': self.model,
            'connector': self.connector,
            'configuration': f"{self.generation} {self.connector}".strip(),
            'product_code': self.product_code,
            'country': self.country_flag,
            'price': self.price
        }

class ApplePencilParser:
    """Парсер для Apple Pencil"""
    
    def __init__(self):
        self.patterns = [
            # Pencil 2 - 7000
            r'Pencil\s+(\d+|Pro|USB\s*C)\s*-\s*(\d+[.,]\d+|\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]*)',
            
            # ✒️Pencil 2 - 7500🇺🇸
            r'✒️Pencil\s+(\d+|Pro|USB\s*C)\s*-\s*(\d+[.,]\d+|\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]+)',
            
            # Apple Pencil 1 🇪🇺 6000
            r'Apple\s+Pencil\s+(\d+|Pro|TYPE-C|USB-C)\s+([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]+)\s+(\d+[.,]\d+|\d+)',
            
            # Apple Pencil TYPE-C 🇪🇺 7000
            r'Apple\s+Pencil\s+(TYPE-C|USB-C)\s+([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]+)\s+(\d+[.,]\d+|\d+)',
        ]

    def parse_lines(self, lines: List[str]) -> Tuple[List[ApplePencilData], List[str]]:
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
                logger.warning(f"Ошибка парсинга строки Apple Pencil: {line} - {e}")
                unparsed_lines.append(line)
        
        return parsed_data, unparsed_lines

    def _parse_single_line(self, line: str) -> ApplePencilData:
        """Парсит одну строку Apple Pencil"""
        for i, pattern in enumerate(self.patterns):
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                groups = match.groups()
                logger.info(f"Apple Pencil паттерн {i} сработал для строки: {line}, групп: {len(groups)}")
                
                try:
                    if i == 0:  # Pencil 2 - 7000
                        generation, price, country = groups
                        model = 'Apple Pencil'
                        connector = self._get_connector_by_generation(generation)
                        
                    elif i == 1:  # ✒️Pencil 2 - 7500🇺🇸
                        generation, price, country = groups
                        model = 'Apple Pencil'
                        connector = self._get_connector_by_generation(generation)
                        
                    elif i == 2:  # Apple Pencil 1 🇪🇺 6000
                        generation, country, price = groups
                        model = 'Apple Pencil'
                        connector = self._get_connector_by_generation(generation)
                        
                    elif i == 3:  # Apple Pencil TYPE-C 🇪🇺 7000
                        connector, country, price = groups
                        model = 'Apple Pencil'
                        generation = self._get_generation_by_connector(connector)
                    
                    # Нормализуем данные
                    generation = self._normalize_generation(generation)
                    connector = self._normalize_connector(connector)
                    price = int(price.replace('.', '').replace(',', ''))
                    
                    return ApplePencilData(
                        model=model,
                        generation=generation,
                        connector=connector,
                        country_flag=country,
                        price=price,
                        source_line=line
                    )
                    
                except Exception as e:
                    logger.error(f"Ошибка парсинга Apple Pencil группы {i}: {e}")
                    continue
        
        return None

    def _get_connector_by_generation(self, generation: str) -> str:
        """Определяет разъем по поколению"""
        gen_lower = generation.lower().replace(' ', '')
        if gen_lower == '1':
            return 'Lightning'
        elif gen_lower == '2':
            return 'Lightning'
        elif gen_lower == 'pro':
            return 'USB-C'
        elif 'usb' in gen_lower or 'type' in gen_lower:
            return 'USB-C'
        return 'Lightning'

    def _get_generation_by_connector(self, connector: str) -> str:
        """Определяет поколение по разъему"""
        conn_lower = connector.lower().replace('-', '').replace(' ', '')
        if 'usbc' in conn_lower or 'typec' in conn_lower:
            return 'USB-C'
        return '2'

    def _normalize_generation(self, generation: str) -> str:
        """Нормализует поколение"""
        gen_lower = generation.lower().replace(' ', '')
        if gen_lower == 'usbс' or gen_lower == 'usbc' or gen_lower == 'type-c':
            return 'USB-C'
        return generation

    def _normalize_connector(self, connector: str) -> str:
        """Нормализует разъем"""
        conn_lower = connector.lower().replace(' ', '').replace('-', '')
        if 'usbc' in conn_lower or 'typec' in conn_lower:
            return 'USB-C'
        return connector

    def _is_apple_pencil_line(self, line: str) -> bool:
        """Проверяет, является ли строка описанием Apple Pencil"""
        line_lower = line.lower()
        
        # Проверяем наличие ключевых слов
        has_pencil = 'pencil' in line_lower and 'vacuum' not in line_lower  # исключаем пылесос
        has_price = bool(re.search(r'\d{4,6}|\d+[.,]\d+', line))
        
        return has_pencil and has_price
