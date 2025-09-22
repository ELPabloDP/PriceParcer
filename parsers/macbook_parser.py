"""
Парсер для MacBook
"""
import re
import logging
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class MacBookPrice:
    """Структура для цены MacBook"""
    source_line: str
    model: str  # Air, Pro
    chip: str   # M1, M2, M3, M4
    size: str   # 13, 15, 14, 16
    memory: str # 8GB, 16GB, 24GB
    storage: str # 256GB, 512GB, 1TB
    color: str  # Gray, Silver, Midnight, Starlight, Sky Blue
    country: str # 🇺🇸, 🇯🇵, etc.
    price: int
    product_code: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Конвертирует в словарь для сохранения"""
        return {
            'firm': 'Apple',
            'device': 'MacBook',
            'generation': f"{self.chip}",
            'variant': self.model,
            'size': self.size,
            'memory': self.memory,
            'storage': self.storage,
            'color': self.color,
            'configuration': f"{self.memory} {self.storage} {self.color}",
            'product_code': self.product_code,
            'country': self.country,
            'price': self.price
        }

class MacBookParser:
    """Парсер для MacBook"""
    
    def __init__(self):
        self.patterns = [
            # MacBook MGN63 Air 13 Space Gray (M1,8GB,256GB)2020 RU/A 51000 🚚
            r'MacBook\s+([A-Z0-9]+)\s+Air\s+(\d+)\s+([^\(]+)\s*\(M(\d+),(\d+)GB,(\d+GB)\)(\d+)\s+([A-Z/]+)\s+(\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]?)\s*([🚚🚛🚘]?)',
            
            # MacBook MC7X4 Air 13 Midnight (M2,16GB,256GB) 2024 64000 🚚
            r'MacBook\s+([A-Z0-9]+)\s+Air\s+(\d+)\s+([^\(]+)\s*\(M(\d+),(\d+)GB,(\d+GB)\)\s+(\d+)\s+(\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]?)\s*([🚚🚛🚘]?)',
            
            # MacBook Air 13 M3: 8/256GB Gray - 69000
            r'MacBook\s+Air\s+(\d+)\s+M(\d+):\s*(\d+)GB/(\d+GB)\s+(\w+)\s*-\s*(\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]?)\s*([🚚🚛🚘]?)',
            
            # MacBook Pro 14 M4: 16/1TB Black - 137000
            r'MacBook\s+Pro\s+(\d+)\s+M(\d+):\s*(\d+)GB/(\d+GB)\s+(\w+)\s*-\s*(\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]?)\s*([🚚🚛🚘]?)',
            
            # MacBook Air 13 M4 (2025) 16/256 Midnight MW123 - 76000🇺🇸
            r'MacBook\s+Air\s+(\d+)\s+M(\d+)\s*\((\d+)\)\s*(\d+)GB/(\d+GB)\s+(\w+)\s+([A-Z0-9]+)\s*-\s*(\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]?)\s*([🚚🚛🚘]?)',
            
            # MacBook Pro 14 M4 (2024) 16/512 Gray MW2U3 - 123000🇺🇸
            r'MacBook\s+Pro\s+(\d+)\s+M(\d+)\s*\((\d+)\)\s*(\d+)GB/(\d+GB)\s+(\w+)\s+([A-Z0-9]+)\s*-\s*(\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]?)\s*([🚚🚛🚘]?)',
            
            # MacBook Pro 16 M4 Max (2024) 36/1TB Silver MX2V3 - 270000🇺🇸
            r'MacBook\s+Pro\s+(\d+)\s+M(\d+)\s+Max\s*\((\d+)\)\s*(\d+)GB/(\d+GB)\s+(\w+)\s+([A-Z0-9]+)\s*-\s*(\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]?)\s*([🚚🚛🚘]?)',
            
            # MacBook Pro 14 M4 Max 16/40 Core 128GB+ 4TB Silve Z1FD0000T 490000
            r'MacBook\s+Pro\s+(\d+)\s+M(\d+)\s+Max\s+(\d+)/(\d+)\s+Core\s+(\d+GB)\+\s+(\d+TB)\s+(\w+)\s+([A-Z0-9]+)\s+(\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]?)\s*([🚚🚛🚘]?)',
            
            # 💻[MWUF3] iMac M4 (8/8/16/256) Blue🇺🇸 — 131500
            r'💻\[([A-Z0-9]+)\]\s+iMac\s+M(\d+)\s*\((\d+)/(\d+)/(\d+)/(\d+)\)\s+(\w+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]?)\s*—\s*(\d+)([🚚🚛🚘]?)',
            
            # 💻[MQTM3] Air 15 (M2 16/1Tb) Midnight🇺🇸 — 116800
            r'💻\[([A-Z0-9]+)\]\s+Air\s+(\d+)\s*\(M(\d+)\s+(\d+)/(\d+TB)\)\s+(\w+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]?)\s*—\s*(\d+)([🚚🚛🚘]?)',
            
            # 💻[MPHF3] Pro 14 M2 (12c CPU/19c GPU/16/1Tb) Gray🇭🇰 — 169000
            r'💻\[([A-Z0-9]+)\]\s+Pro\s+(\d+)\s+M(\d+)\s*\((\d+)c\s+CPU/(\d+)c\s+GPU/(\d+)/(\d+TB)\)\s+(\w+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]?)\s*—\s*(\d+)([🚚🚛🚘]?)',
            
            # MacBook MGN63 Air 13 Space Gray (M1,8GB,256GB)2020 RU/A 50500 🚚
            r'MacBook\s+([A-Z0-9]+)\s+Air\s+(\d+)\s+([^\(]+)\s*\(M(\d+),(\d+)GB,(\d+GB)\)(\d+)\s+([A-Z/]+)\s+(\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]?)\s*([🚚🚛🚘]?)',
            
            # MacBook MC7X4 Air 13 Midnight (M2,16GB,256GB) 2024 64000 🚚
            r'MacBook\s+([A-Z0-9]+)\s+Air\s+(\d+)\s+([^\(]+)\s*\(M(\d+),(\d+)GB,(\d+GB)\)\s+(\d+)\s+(\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]?)\s*([🚚🚛🚘]?)',
            
            # MacBook MC6K4 Air 15 Starlight (M4, 24GB, 512GB) 2025 🇺🇸 125000
            r'MacBook\s+([A-Z0-9]+)\s+Air\s+(\d+)\s+([^\(]+)\s*\(M(\d+),\s*(\d+)GB,\s*(\d+GB)\)\s+(\d+)\s+([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]?)\s+(\d+)([🚚🚛🚘]?)',
            
            # MacBook MC8P4 Air 13 Starlight (M3, 24GB, 512GB) 2024 88500
            r'MacBook\s+([A-Z0-9]+)\s+Air\s+(\d+)\s+([^\(]+)\s*\(M(\d+),\s*(\d+)GB,\s*(\d+GB)\)\s+(\d+)\s+(\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]?)\s*([🚚🚛🚘]?)',
            
            # MacBook MW0Y3 Air 13 Starlight (M4, 16GB, 256GB) 2025 74100 🚚
            r'MacBook\s+([A-Z0-9]+)\s+Air\s+(\d+)\s+([^\(]+)\s*\(M(\d+),\s*(\d+)GB,\s*(\d+GB)\)\s+(\d+)\s+(\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]?)\s*([🚚🚛🚘]?)',
            
            # MacBook MC654 Air 13 Silver (M4, 24GB, 512GB) 2025 109200
            r'MacBook\s+([A-Z0-9]+)\s+Air\s+(\d+)\s+([^\(]+)\s*\(M(\d+),\s*(\d+)GB,\s*(\d+GB)\)\s+(\d+)\s+(\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]?)\s*([🚚🚛🚘]?)',
            
            # MacBook MW1J3 Air 15 Starlight (M4, 16GB, 256GB) 2025 92200
            r'MacBook\s+([A-Z0-9]+)\s+Air\s+(\d+)\s+([^\(]+)\s*\(M(\d+),\s*(\d+)GB,\s*(\d+GB)\)\s+(\d+)\s+(\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]?)\s*([🚚🚛🚘]?)',
            
            # MacBook MC6K4 Air 15 Starlight (M4, 24GB, 512GB) 2025 125000
            r'MacBook\s+([A-Z0-9]+)\s+Air\s+(\d+)\s+([^\(]+)\s*\(M(\d+),\s*(\d+)GB,\s*(\d+GB)\)\s+(\d+)\s+(\d+)([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]?)\s*([🚚🚛🚘]?)',
            
            # MacBook MC6K4 Air 15 Starlight (M4, 24GB, 512GB) 2025 🇺🇸 125000
            r'MacBook\s+([A-Z0-9]+)\s+Air\s+(\d+)\s+([^\(]+)\s*\(M(\d+),\s*(\d+)GB,\s*(\d+GB)\)\s+(\d+)\s+([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳])\s+(\d+)([🚚🚛🚘]?)',
            
            # MacBook MC6K4 Air 15 Starlight (M4, 24GB, 512GB) 2025 🇺🇸 125000 (альтернативный паттерн)
            r'MacBook\s+([A-Z0-9]+)\s+Air\s+(\d+)\s+([^\(]+)\s*\(M(\d+),\s*(\d+)GB,\s*(\d+GB)\)\s+(\d+)\s+([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳])\s+(\d+)([🚚🚛🚘]?)',
            
            # MacBook MC6K4 Air 15 Starlight (M4, 24GB, 512GB) 2025 🇺🇸 125000 (с пробелом перед флагом)
            r'MacBook\s+([A-Z0-9]+)\s+Air\s+(\d+)\s+([^\(]+)\s*\(M(\d+),\s*(\d+)GB,\s*(\d+GB)\)\s+(\d+)\s+([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳])\s+(\d+)([🚚🚛🚘]?)',
            
            # Универсальный паттерн для MacBook с флагом страны
            r'MacBook\s+([A-Z0-9]+)\s+Air\s+(\d+)\s+([^\(]+)\s*\(M(\d+),\s*(\d+)GB,\s*(\d+GB)\)\s+(\d+)\s+([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳])\s+(\d+)',
        ]
        
        # Цвета MacBook
        self.colors = {
            'Gray': 'Gray',
            'Silver': 'Silver', 
            'Midnight': 'Midnight',
            'Starlight': 'Starlight',
            'Sky': 'Sky Blue',
            'Blue': 'Sky Blue',
            'Black': 'Space Black',
            'Space': 'Space Gray'
        }

    def _is_macbook_line(self, line: str) -> bool:
        """Проверяет, является ли строка MacBook"""
        line_lower = line.lower()
        
        # Проверяем наличие MacBook или чипов
        has_macbook = 'macbook' in line_lower or re.search(r'm[1-4]', line_lower)
        
        # Проверяем наличие цены (4-6 цифр)
        has_price = bool(re.search(r'\d{4,6}', line))
        
        # Проверяем наличие конфигурации (GB/TB)
        has_config = 'gb' in line_lower or 'tb' in line_lower
        
        # Исключаем ненужные строки
        exclude_keywords = ['гарантия', 'активаций', 'adapter', 'от 10 шт', 'mouse', 'trackpad', 'pencil']
        has_exclude = any(keyword in line_lower for keyword in exclude_keywords)
        
        return has_macbook and has_price and has_config and not has_exclude

    def _extract_country(self, line: str) -> str:
        """Извлекает страну из строки"""
        country_match = re.search(r'([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳])', line)
        return country_match.group(1) if country_match else ''

    def _normalize_color(self, color: str) -> str:
        """Нормализует цвет"""
        for key, value in self.colors.items():
            if key.lower() in color.lower():
                return value
        return color

    def _normalize_storage(self, storage: str) -> str:
        """Нормализует объем хранилища"""
        if 'TB' in storage.upper():
            return storage.upper()
        elif 'GB' in storage.upper():
            return storage.upper()
        else:
            return f"{storage}GB"

    def parse_lines(self, lines: List[str]) -> Tuple[List[MacBookPrice], List[str]]:
        """Парсит строки с MacBook"""
        parsed_prices = []
        unparsed_lines = []
        
        for line in lines:
            line = line.strip()
            if not line or not self._is_macbook_line(line):
                unparsed_lines.append(line)
                continue
                
            try:
                price = self._parse_single_line(line)
                if price:
                    parsed_prices.append(price)
                else:
                    unparsed_lines.append(line)
            except Exception as e:
                logger.warning(f"Ошибка парсинга строки MacBook: {line} - {e}")
                unparsed_lines.append(line)
        
        return parsed_prices, unparsed_lines

    def _parse_single_line(self, line: str) -> MacBookPrice:
        """Парсит одну строку MacBook"""
        for i, pattern in enumerate(self.patterns):
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                groups = match.groups()
                
                try:
                    if i == 0:  # MacBook MGN63 Air 13 Space Gray (M1,8GB,256GB)2020 RU/A 51000 🚚
                        product_code, size, color, chip, memory, storage, year, region, price, country, delivery = groups
                        model = 'Air'
                        if not country:
                            country = self._extract_country(line)
                        
                    elif i == 1:  # MacBook MC7X4 Air 13 Midnight (M2,16GB,256GB) 2024 64000 🚚
                        product_code, size, color, chip, memory, storage, year, price, country, delivery = groups
                        model = 'Air'
                        if not country:
                            country = self._extract_country(line)
                            
                    elif i == 2:  # MacBook Air 13 M3: 8/256GB Gray - 69000
                        size, chip, memory, storage, color, price, country, delivery = groups
                        model = 'Air'
                        product_code = ""
                        if not country:
                            country = self._extract_country(line)
                            
                    elif i == 3:  # MacBook Pro 14 M4: 16/1TB Black - 137000
                        size, chip, memory, storage, color, price, country, delivery = groups
                        model = 'Pro'
                        product_code = ""
                        if not country:
                            country = self._extract_country(line)
                            
                    elif i == 4:  # MacBook Air 13 M4 (2025) 16/256 Midnight MW123 - 76000🇺🇸
                        size, chip, year, memory, storage, color, product_code, price, country, delivery = groups
                        model = 'Air'
                        if not country:
                            country = self._extract_country(line)
                            
                    elif i == 5:  # MacBook Pro 14 M4 (2024) 16/512 Gray MW2U3 - 123000🇺🇸
                        size, chip, year, memory, storage, color, product_code, price, country, delivery = groups
                        model = 'Pro'
                        if not country:
                            country = self._extract_country(line)
                            
                    elif i == 6:  # MacBook Pro 16 M4 Max (2024) 36/1TB Silver MX2V3 - 270000🇺🇸
                        size, chip, year, memory, storage, color, product_code, price, country, delivery = groups
                        model = 'Pro'
                        if not country:
                            country = self._extract_country(line)
                            
                    elif i == 7:  # MacBook Pro 14 M4 Max 16/40 Core 128GB+ 4TB Silve Z1FD0000T 490000
                        size, chip, cpu_cores, gpu_cores, memory, storage, color, product_code, price, country, delivery = groups
                        model = 'Pro'
                        if not country:
                            country = self._extract_country(line)
                            
                    elif i == 8:  # 💻[MWUF3] iMac M4 (8/8/16/256) Blue🇺🇸 — 131500
                        product_code, chip, cpu_cores, gpu_cores, memory, storage, color, country, price, delivery = groups
                        model = 'iMac'
                        size = '24'  # iMac всегда 24 дюйма
                        if not country:
                            country = self._extract_country(line)
                            
                    elif i == 9:  # 💻[MQTM3] Air 15 (M2 16/1Tb) Midnight🇺🇸 — 116800
                        product_code, size, chip, memory, storage, color, country, price, delivery = groups
                        model = 'Air'
                        if not country:
                            country = self._extract_country(line)
                            
                    elif i == 10:  # 💻[MPHF3] Pro 14 M2 (12c CPU/19c GPU/16/1Tb) Gray🇭🇰 — 169000
                        product_code, size, chip, cpu_cores, gpu_cores, memory, storage, color, country, price, delivery = groups
                        model = 'Pro'
                        if not country:
                            country = self._extract_country(line)
                            
                    elif i == 11:  # MacBook MGN63 Air 13 Space Gray (M1,8GB,256GB)2020 RU/A 50500 🚚
                        product_code, size, color, chip, memory, storage, year, region, price, country, delivery = groups
                        model = 'Air'
                        if not country:
                            country = self._extract_country(line)
                            
                    elif i == 12:  # MacBook MC7X4 Air 13 Midnight (M2,16GB,256GB) 2024 64000 🚚
                        product_code, size, color, chip, memory, storage, year, price, country, delivery = groups
                        model = 'Air'
                        if not country:
                            country = self._extract_country(line)
                            
                    elif i == 13:  # MacBook MC6K4 Air 15 Starlight (M4, 24GB, 512GB) 2025 🇺🇸 125000
                        product_code, size, color, chip, memory, storage, year, country, price, delivery = groups
                        model = 'Air'
                        if not country:
                            country = self._extract_country(line)
                            
                    elif i == 14:  # MacBook MC8P4 Air 13 Starlight (M3, 24GB, 512GB) 2024 88500
                        product_code, size, color, chip, memory, storage, year, price, country, delivery = groups
                        model = 'Air'
                        if not country:
                            country = self._extract_country(line)
                            
                    elif i == 16:  # MacBook MW0Y3 Air 13 Starlight (M4, 16GB, 256GB) 2025 74100 🚚
                        product_code, size, color, chip, memory, storage, year, price, country, delivery = groups
                        model = 'Air'
                        if not country:
                            country = self._extract_country(line)
                            
                    elif i == 17:  # MacBook MC654 Air 13 Silver (M4, 24GB, 512GB) 2025 109200
                        product_code, size, color, chip, memory, storage, year, price, country, delivery = groups
                        model = 'Air'
                        if not country:
                            country = self._extract_country(line)
                            
                    elif i == 18:  # MacBook MW1J3 Air 15 Starlight (M4, 16GB, 256GB) 2025 92200
                        product_code, size, color, chip, memory, storage, year, price, country, delivery = groups
                        model = 'Air'
                        if not country:
                            country = self._extract_country(line)
                            
                    elif i == 19:  # MacBook MC6K4 Air 15 Starlight (M4, 24GB, 512GB) 2025 125000
                        product_code, size, color, chip, memory, storage, year, price, country, delivery = groups
                        model = 'Air'
                        if not country:
                            country = self._extract_country(line)
                            
                    elif i == 20:  # MacBook MC6K4 Air 15 Starlight (M4, 24GB, 512GB) 2025 🇺🇸 125000
                        product_code, size, color, chip, memory, storage, year, country, price, delivery = groups
                        model = 'Air'
                        if not country:
                            country = self._extract_country(line)
                            
                    elif i == 21:  # MacBook MC6K4 Air 15 Starlight (M4, 24GB, 512GB) 2025 🇺🇸 125000 (альтернативный паттерн)
                        product_code, size, color, chip, memory, storage, year, country, price, delivery = groups
                        model = 'Air'
                        if not country:
                            country = self._extract_country(line)
                            
                    elif i == 22:  # MacBook MC6K4 Air 15 Starlight (M4, 24GB, 512GB) 2025 🇺🇸 125000 (с пробелом перед флагом)
                        product_code, size, color, chip, memory, storage, year, country, price, delivery = groups
                        model = 'Air'
                        if not country:
                            country = self._extract_country(line)
                            
                    elif i == 23:  # Универсальный паттерн для MacBook с флагом страны
                        product_code, size, color, chip, memory, storage, year, country, price = groups
                        model = 'Air'
                        delivery = ''
                        if not country:
                            country = self._extract_country(line)
                    
                    else:
                        continue
                    
                    # Нормализуем данные
                    color = self._normalize_color(color)
                    storage = self._normalize_storage(storage)
                    memory = f"{memory}GB"
                    
                    return MacBookPrice(
                        source_line=line,
                        model=model,
                        chip=f"M{chip}",
                        size=size,
                        memory=memory,
                        storage=storage,
                        color=color,
                        country=country,
                        price=int(price),
                        product_code=product_code
                    )
                    
                except (ValueError, IndexError) as e:
                    logger.warning(f"Ошибка парсинга MacBook группы {i}: {e} - {line}")
                    continue
        
        return None

# Создаем экземпляр парсера
macbook_parser = MacBookParser()
