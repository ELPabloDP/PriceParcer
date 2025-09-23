"""
Парсер для iMac
"""
import re
import logging
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class iMacData:
    """Структура данных для цены iMac"""
    model: str  # iMac, Mac Mini
    chip: str   # M1, M2, M3, M4
    size: str   # 24, Mini
    memory: str # 8GB, 16GB, 24GB
    storage: str # 256GB, 512GB, 1TB
    color: str  # Blue, Silver, etc.
    country_flag: str  # 🇺🇸, 🇯🇵, etc.
    price: int
    product_code: str = ""
    source_line: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Конвертирует в словарь для сохранения"""
        return {
            'firm': 'Apple',
            'device': self.model,
            'generation': f"{self.chip}",
            'variant': self.size,
            'memory': self.memory,
            'storage': self.storage,
            'color': self.color,
            'configuration': f"{self.memory} {self.storage} {self.color}",
            'product_code': self.product_code,
            'country': self.country_flag,
            'price': self.price
        }

class iMacParser:
    """Парсер для iMac"""
    
    def __init__(self):
        self.patterns = [
            # 💻[MWUF3] iMac M4 (8/8/16/256) Blue🇺🇸 — 131500
            r'💻\[([A-Z0-9]+)\]\s+iMac\s+M(\d+)\s*\((\d+)/(\d+)/(\d+)/(\d+)\)\s+(\w+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]+)\s*—\s*(\d+[.,]\d+|\d+)',
            
            # Mac Mini M2 Pro MNH73 - 70000🇺🇸
            r'Mac\s+Mini\s+M(\d+)\s+Pro\s+([A-Z0-9]+)\s*-\s*(\d+[.,]\d+|\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]+)',
            
            # Mac Mini (MU9D3) M4/16/256 Silver 🇨🇳 48500
            r'Mac\s+Mini\s*\(([A-Z0-9]+)\)\s+M(\d+)/(\d+)/(\d+)\s+(\w+)\s+([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]+)\s+(\d+[.,]\d+|\d+)',
            
            # M2 8/256GB - 30000
            r'M(\d+)\s+(\d+)/(\d+(?:GB|TB)?)\s*-\s*(\d+[.,]\d+|\d+)',
        ]
        
        # Цвета iMac
        self.colors = {
            'blue': 'Blue',
            'silver': 'Silver',
            'green': 'Green',
            'pink': 'Pink',
            'yellow': 'Yellow',
            'orange': 'Orange',
            'purple': 'Purple'
        }

    def parse_lines(self, lines: List[str]) -> Tuple[List[iMacData], List[str]]:
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
                logger.warning(f"Ошибка парсинга строки iMac: {line} - {e}")
                unparsed_lines.append(line)
        
        return parsed_data, unparsed_lines

    def _parse_single_line(self, line: str) -> iMacData:
        """Парсит одну строку iMac"""
        for i, pattern in enumerate(self.patterns):
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                groups = match.groups()
                logger.info(f"iMac паттерн {i} сработал для строки: {line}, групп: {len(groups)}")
                
                try:
                    if i == 0:  # 💻[MWUF3] iMac M4 (8/8/16/256) Blue🇺🇸 — 131500
                        product_code, chip, cpu_cores, gpu_cores, memory, storage, color, country, price = groups
                        model = 'iMac'
                        size = '24'  # iMac всегда 24 дюйма
                        
                    elif i == 1:  # Mac Mini M2 Pro MNH73 - 70000🇺🇸
                        chip, product_code, price, country = groups
                        model = 'Mac Mini'
                        size = 'Mini'
                        memory = '16'  # Pro версия обычно 16GB
                        storage = '512'  # По умолчанию
                        color = 'Silver'
                        
                    elif i == 2:  # Mac Mini (MU9D3) M4/16/256 Silver 🇨🇳 48500
                        product_code, chip, memory, storage, color, country, price = groups
                        model = 'Mac Mini'
                        size = 'Mini'
                        
                    elif i == 3:  # M2 8/256GB - 30000
                        chip, memory, storage, price = groups
                        model = 'Mac Mini'
                        size = 'Mini'
                        color = 'Silver'
                        country = ''
                        product_code = ''
                    
                    # Нормализуем данные
                    color = self._normalize_color(color)
                    storage = self._normalize_storage(storage)
                    memory = f"{memory}GB"
                    price = int(price.replace('.', '').replace(',', ''))
                    
                    return iMacData(
                        model=model,
                        chip=f"M{chip}",
                        size=size,
                        memory=memory,
                        storage=storage,
                        color=color,
                        country_flag=country,
                        price=price,
                        product_code=product_code,
                        source_line=line
                    )
                    
                except Exception as e:
                    logger.error(f"Ошибка парсинга iMac группы {i}: {e}")
                    continue
        
        return None

    def _normalize_color(self, color: str) -> str:
        """Нормализует цвет"""
        color_lower = color.lower().strip()
        return self.colors.get(color_lower, color.title())

    def _normalize_storage(self, storage: str) -> str:
        """Нормализует объем накопителя"""
        storage = storage.strip()
        if not storage.endswith(('GB', 'TB')):
            if int(storage) >= 1000:
                storage = f"{int(storage)//1000}TB"
            else:
                storage = f"{storage}GB"
        return storage

    def _is_imac_line(self, line: str) -> bool:
        """Проверяет, является ли строка описанием iMac"""
        line_lower = line.lower()
        
        # Проверяем наличие ключевых слов
        has_imac = 'imac' in line_lower or 'mac mini' in line_lower
        has_chip = bool(re.search(r'm[1-4]', line_lower))
        has_price = bool(re.search(r'\d{4,6}|\d+[.,]\d+', line))
        
        return has_imac and (has_chip or has_price)
