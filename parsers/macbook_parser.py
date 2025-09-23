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
            # Новый формат: 🇺🇸 MGND3 - 8/256 Gold — 62.000₽ (проверяем первым!)
            r'([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]+)\s+([A-Z0-9]+)\s*-\s*(\d+)/(\d+)\s+(\w+)\s*—\s*(\d+[.,]\d+|\d+)\s*₽?',
            
            # Короткий формат: MW0Y3 13" M4 10/8 16 256GB Starlight - 80.000
            r'([A-Z0-9]+)\s+(\d+)"\s+M(\d+)\s+(\d+)/(\d+)\s+(\d+)\s+(\d+(?:GB|TB|Gb|Tb))\s+(\w+)\s*-\s*(\d+[.,]\d+|\d+)',
            
            # С флагом впереди: 🇺🇸MW0X3 13" M4 10/10 16 512GB Silver - 99.000
            r'([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]+)([A-Z0-9]+)\s+(\d+)"\s+M(\d+)\s+(\d+)/(\d+)\s+(\d+)\s+(\d+(?:GB|TB|Gb|Tb))\s+(\w+)\s*-\s*(\d+[.,]\d+|\d+)',
            
            # С эмодзи: 💻Z1GS000NK MacBook Air 13 M4 10/10 24Gb 1Tb Silver - 185.000
            r'💻([A-Z0-9]+)\s+MacBook\s+Air\s+(\d+)\s+M(\d+)\s+(\d+)/(\d+)\s+(\d+(?:GB|Gb))\s+(\d+(?:TB|Tb|GB|Gb))\s+(\w+)\s*-\s*(\d+[.,]\d+|\d+)',
            
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
            r'MacBook\s+([A-Z0-9]+)\s+Air\s+(\d+)\s+([^\(]+)\s*\(M(\d+),\s*(\d+)GB,\s*(\d+GB)\)\s+(\d+)\s+([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇤🇷🇪🇺🇷🇺🇨🇦🇻🇳])\s+(\d+)',
            
            # ========= НОВЫЕ ПАТТЕРНЫ =========
            # Короткий формат: MW0Y3 13" M4 10/8 16 256GB Starlight - 80.000
            r'([A-Z0-9]+)\s+(\d+)"\s+M(\d+)\s+(\d+)/(\d+)\s+(\d+)\s+(\d+(?:GB|TB|Gb|Tb))\s+(\w+)\s*-\s*(\d+[.,]\d+|\d+)',
            
            # С флагом впереди: 🇺🇸MW0X3 13" M4 10/10 16 512GB Silver - 99.000
            r'([🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇤🇷🇪🇺🇷🇺🇨🇦🇻🇳]+)([A-Z0-9]+)\s+(\d+)"\s+M(\d+)\s+(\d+)/(\d+)\s+(\d+)\s+(\d+(?:GB|TB|Gb|Tb))\s+(\w+)\s*-\s*(\d+[.,]\d+|\d+)',
            
            # С эмодзи: 💻Z1GS000NK MacBook Air 13 M4 10/10 24Gb 1Tb Silver - 185.000
            r'💻([A-Z0-9]+)\s+MacBook\s+Air\s+(\d+)\s+M(\d+)\s+(\d+)/(\d+)\s+(\d+(?:GB|Gb))\s+(\d+(?:TB|Tb|GB|Gb))\s+(\w+)\s*-\s*(\d+[.,]\d+|\d+)',
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
        has_macbook = 'macbook' in line_lower or bool(re.search(r'm[1-4]', line_lower))
        
        # Проверяем наличие цены (4-6 цифр или с точками/запятыми)
        has_price = bool(re.search(r'\d{4,6}|\d+[.,]\d+', line))
        
        # Проверяем наличие конфигурации (GB/TB) или новый формат с флагом
        has_config = 'gb' in line_lower or 'tb' in line_lower
        has_flag_format = bool(re.search(r'[🇺🇸🇯🇵🇮🇳🇨🇳🇦🇪🇭🇰🇰🇷🇪🇺🇷🇺🇨🇦🇻🇳]+\s+[A-Z0-9]+\s*-\s*\d+/\d+', line))
        
        # Исключаем ненужные строки
        exclude_keywords = ['гарантия', 'активаций', 'adapter', 'от 10 шт', 'mouse', 'trackpad', 'pencil']
        has_exclude = any(keyword in line_lower for keyword in exclude_keywords)
        
        # Для нового формата достаточно флага + кода + конфигурации + цены
        if has_flag_format and has_price and not has_exclude:
            logger.info(f"MacBook строка распознана (новый формат): {line}")
            return True
        
        # Для обычного формата нужен MacBook + конфигурация + цена
        result = has_macbook and has_price and has_config and not has_exclude
        if result:
            logger.info(f"MacBook строка распознана (обычный формат): {line}")
        return result

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
    
    def _extract_context_from_previous_lines(self, lines: List[str], current_index: int) -> Dict[str, str]:
        """Извлекает контекст из предыдущих строк для определения модели, чипа и размера"""
        context = {'model': 'Air', 'chip': 'M1', 'size': '13'}
        
        # Ищем в предыдущих 5 строках
        start_index = max(0, current_index - 5)
        for i in range(start_index, current_index):
            if i < len(lines):
                line = lines[i].strip()
                line_lower = line.lower()
                
                # Ищем модель
                if 'macbook air' in line_lower:
                    context['model'] = 'Air'
                    # Ищем размер
                    size_match = re.search(r'air\s+(\d+)', line_lower)
                    if size_match:
                        context['size'] = size_match.group(1)
                elif 'macbook pro' in line_lower:
                    context['model'] = 'Pro'
                    # Ищем размер
                    size_match = re.search(r'pro\s+(\d+)', line_lower)
                    if size_match:
                        context['size'] = size_match.group(1)
                
                # Ищем чип
                chip_match = re.search(r'm(\d+)', line_lower)
                if chip_match:
                    context['chip'] = f"M{chip_match.group(1)}"
        
        return context

    def parse_lines(self, lines: List[str]) -> Tuple[List[MacBookPrice], List[str]]:
        """Парсит строки с MacBook"""
        parsed_prices = []
        unparsed_lines = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line or not self._is_macbook_line(line):
                unparsed_lines.append(line)
                continue
                
            try:
                price = self._parse_single_line(line, lines, i)
                if price:
                    parsed_prices.append(price)
                else:
                    unparsed_lines.append(line)
            except Exception as e:
                logger.warning(f"Ошибка парсинга строки MacBook: {line} - {e}")
                unparsed_lines.append(line)
        
        return parsed_prices, unparsed_lines

    def _parse_single_line(self, line: str, lines: List[str] = None, current_index: int = 0) -> MacBookPrice:
        """Парсит одну строку MacBook"""
        for i, pattern in enumerate(self.patterns):
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                groups = match.groups()
                logger.info(f"MacBook паттерн {i} сработал для строки: {line}, групп: {len(groups)}")
                
                try:
                    if i == 0:  # Новый формат: 🇺🇸 MGND3 - 8/256 Gold — 62.000₽
                        country, product_code, memory, storage, color, price = groups
                        # Извлекаем контекст из предыдущих строк
                        if lines and current_index is not None:
                            context = self._extract_context_from_previous_lines(lines, current_index)
                            model = context['model']
                            chip = context['chip']
                            size = context['size']
                        else:
                            model = 'Air'
                            chip = 'M1'
                            size = '13'
                        delivery = ''
                        # Нормализуем цену (убираем точки и запятые)
                        price = price.replace('.', '').replace(',', '')
                        # Добавляем GB к storage если его нет
                        if not storage.endswith('GB'):
                            storage = f"{storage}GB"
                            
                    elif i == 1:  # MacBook MGN63 Air 13 Space Gray (M1,8GB,256GB)2020 RU/A 51000 🚚
                        product_code, size, color, chip, memory, storage, year, region, price, country, delivery = groups
                        model = 'Air'
                        if not country:
                            country = self._extract_country(line)
                        
                    elif i == 5:  # MacBook MC7X4 Air 13 Midnight (M2,16GB,256GB) 2024 64000 🚚
                        product_code, size, color, chip, memory, storage, year, price, country, delivery = groups
                        model = 'Air'
                        if not country:
                            country = self._extract_country(line)
                            
                    elif i == 6:  # MacBook Air 13 M3: 8/256GB Gray - 69000
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
                            
                    elif i == 23:  # Новый формат: 🇺🇸 MGND3 - 8/256 Gold — 62.000₽
                        country, product_code, memory, storage, color, price = groups
                        # Извлекаем контекст из предыдущих строк
                        if lines and current_index is not None:
                            context = self._extract_context_from_previous_lines(lines, current_index)
                            model = context['model']
                            chip = context['chip']
                            size = context['size']
                        else:
                            model = 'Air'
                            chip = 'M1'
                            size = '13'
                        delivery = ''
                        # Нормализуем цену (убираем точки и запятые)
                        price = price.replace('.', '').replace(',', '')
                        # Добавляем GB к storage если его нет
                        if not storage.endswith('GB'):
                            storage = f"{storage}GB"
                    
                    elif i == 24:  # Универсальный паттерн для MacBook с флагом страны
                        product_code, size, color, chip, memory, storage, year, country, price = groups
                        model = 'Air'
                        delivery = ''
                        if not country:
                            country = self._extract_country(line)
                    
                    elif i == 25:  # Короткий формат: MW0Y3 13" M4 10/8 16 256GB Starlight - 80.000
                        product_code, size, chip, cpu_cores, gpu_cores, memory, storage, color, price = groups
                        model = 'Air'
                        country = ''
                        delivery = ''
                        price = price.replace('.', '').replace(',', '')
                        
                    elif i == 26:  # С флагом впереди: 🇺🇸MW0X3 13" M4 10/10 16 512GB Silver - 99.000
                        country, product_code, size, chip, cpu_cores, gpu_cores, memory, storage, color, price = groups
                        model = 'Air'
                        delivery = ''
                        price = price.replace('.', '').replace(',', '')
                        
                    elif i == 27:  # С эмодзи: 💻Z1GS000NK MacBook Air 13 M4 10/10 24Gb 1Tb Silver - 185.000
                        product_code, size, chip, cpu_cores, gpu_cores, memory, storage, color, price = groups
                        model = 'Air'
                        country = ''
                        delivery = ''
                        price = price.replace('.', '').replace(',', '')
                    
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
                    logger.warning(f"Группы: {groups}")
                    continue
        
        return None

# Создаем экземпляр парсера
macbook_parser = MacBookParser()
