import re
import logging

logger = logging.getLogger(__name__)

class AppleWatchParser:
    """Парсер для Apple Watch"""
    
    def __init__(self):
        # Паттерны для разных типов Apple Watch
        self.patterns = [
            # Apple Watch SE 40 Midnight S/M 2024 16300
            r'apple\s+watch\s+se\s+(\d+)\s+(\w+)\s+([^0-9]+?)\s+(\d{4})\s+([\d.,]+)',
            
            # Apple Watch SE 40 Silver S/M 2024 MXEC3 16100
            r'apple\s+watch\s+se\s+(\d+)\s+(\w+)\s+([^0-9]+?)\s+(\d{4})\s+([a-z0-9]+)\s+([\d.,]+)',
            
            # Apple Watch S10 42 Rose Gold Al LB S/M GPS MWWH3 28000
            r'apple\s+watch\s+s(\d+)\s+(\d+)\s+([^0-9]+?)\s+([^0-9]+?)\s+([^0-9]+?)\s+([^0-9]+?)\s+([^0-9]+?)\s+([a-z0-9]+)\s+([\d.,]+)',
            
            # Apple Watch S10 46 Jet Black M/L Q3LW 33500
            r'apple\s+watch\s+s(\d+)\s+(\d+)\s+([^0-9]+?)\s+([^0-9]+?)\s+([a-z0-9]+)\s+([\d.,]+)',
            
            # Apple Watch Ultra 2 49 Blue/Black (S/M) 56200
            r'apple\s+watch\s+ultra\s+(\d+)\s+(\d+)\s+([^0-9]+?)\s+\(([^)]+)\)\s+([\d.,]+)',
            
            # Apple Watch Ultra 2 49 Green/Gray (S/M) MRFN3 56200
            r'apple\s+watch\s+ultra\s+(\d+)\s+(\d+)\s+([^0-9]+?)\s+\(([^)]+)\)\s+([a-z0-9]+)\s+([\d.,]+)',
            
            # AW SE 2024 40mm Midnight SB Midnight S/M - 16500
            r'aw\s+se\s+(\d{4})\s+(\d+)mm\s+(\w+)\s+([^0-9]+?)\s+([^0-9]+?)\s+([^0-9]+?)\s*[-–]\s*([\d.,]+)',
            
            # AW S10 42 Rose Gold S/M 27900🇺🇸
            r'aw\s+s(\d+)\s+(\d+)\s+([^0-9]+?)\s+([^0-9]+?)\s+([\d.,]+)([🇺🇸🇯🇵🇮🇳🇪🇺🇦🇪🇨🇦🇻🇳]*)',
            
            # AW 10 42 Rose Gold S/M 27900🇺🇸 (без S)
            r'aw\s+(\d+)\s+(\d+)\s+([^0-9]+?)\s+([^0-9]+?)\s+([\d.,]+)([🇺🇸🇯🇵🇮🇳🇪🇺🇦🇪🇨🇦🇻🇳]*)',
            
            # AW 10 42 Gold Titanium Milanese Loop 59500🇺🇸
            r'aw\s+(\d+)\s+(\d+)\s+([^0-9]+?)\s+([^0-9]+?)\s+([^0-9]+?)\s+([\d.,]+)([🇺🇸🇯🇵🇮🇳🇪🇺🇦🇪🇨🇦🇻🇳]*)',
            
            # AW 10 46mm Silver Sport Loop 30500🇺🇸 (с mm)
            r'aw\s+(\d+)\s+(\d+)mm\s+([^0-9]+?)\s+([^0-9]+?)\s+([\d.,]+)([🇺🇸🇯🇵🇮🇳🇪🇺🇦🇪🇨🇦🇻🇳]*)',
            
            # AW Ultra 2 49 Trail Blue/Black S/M 58400🇺🇸
            r'aw\s+ultra\s+(\d+)\s+(\d+)\s+([^0-9]+?)\s+([^0-9]+?)\s+([\d.,]+)([🇺🇸🇯🇵🇮🇳🇪🇺🇦🇪🇨🇦🇻🇳]*)',
            
            # 🇺🇸 AW SE 2024 40mm Midnight SB Midnight S/M - 16500
            r'([🇺🇸🇯🇵🇮🇳🇪🇺🇦🇪🇨🇦🇻🇳]*)\s*aw\s+se\s+(\d{4})\s+(\d+)mm\s+(\w+)\s+([^0-9]+?)\s+([^0-9]+?)\s+([^0-9]+?)\s*[-–]\s*([\d.,]+)',
            
            # 🇺🇸 AW S10 46mm Silver SB Denim M/L - 29500
            r'([🇺🇸🇯🇵🇮🇳🇪🇺🇦🇪🇨🇦🇻🇳]*)\s*aw\s+s(\d+)\s+(\d+)mm\s+([^0-9]+?)\s+([^0-9]+?)\s+([^0-9]+?)\s*[-–]\s*([\d.,]+)',
            
            # 🇺🇸 AW Ultra 2 2024 Black Dark Green Alpine Loop S - 59000
            r'([🇺🇸🇯🇵🇮🇳🇪🇺🇦🇪🇨🇦🇻🇳]*)\s*aw\s+ultra\s+(\d+)\s+(\d{4})\s+([^0-9]+?)\s+([^0-9]+?)\s+([^0-9]+?)\s*[-–]\s*([\d.,]+)',
        ]
        
        # Маппинг цветов корпуса
        self.case_colors = {
            'midnight': 'Midnight',
            'silver': 'Silver',
            'starlight': 'Starlight',
            'rose': 'Rose Gold',
            'rose gold': 'Rose Gold',
            'jet': 'Jet Black',
            'jet black': 'Jet Black',
            'black': 'Space Black',
            'space black': 'Space Black',
            'natural': 'Natural Titanium',
            'natural titanium': 'Natural Titanium',
            'blue': 'Blue',
            'green': 'Green',
            'gray': 'Gray',
            'grey': 'Gray',
            'titanium': 'Titanium',
            'orange': 'Orange',
            'indigo': 'Indigo',
        }
        
        # Маппинг типов ремешков
        self.band_types = {
            'sb': 'Sport Band',
            'sl': 'Sport Loop',
            'sport band': 'Sport Band',
            'sport loop': 'Sport Loop',
            'milanese': 'Milanese Loop',
            'milanese loop': 'Milanese Loop',
            'ocean': 'Ocean Band',
            'ocean band': 'Ocean Band',
            'alpine': 'Alpine Loop',
            'alpine loop': 'Alpine Loop',
            'trail': 'Trail Loop',
            'trail loop': 'Trail Loop',
        }
        
        # Маппинг цветов ремешков
        self.band_colors = {
            'midnight': 'Midnight',
            'silver': 'Silver',
            'starlight': 'Starlight',
            'lake green': 'Lake Green',
            'denim': 'Denim',
            'blue': 'Blue',
            'black': 'Black',
            'dark green': 'Dark Green',
            'navy': 'Navy',
            'orange': 'Orange',
            'beige': 'Beige',
            'indigo': 'Indigo',
            'plum': 'Plum',
            'blue cloud': 'Blue Cloud',
            'natural': 'Natural',
            'navi': 'Navy',
        }
        
        # Маппинг размеров ремешков
        self.band_sizes = {
            's/m': 'S/M',
            'm/l': 'M/L',
            's': 'S',
            'm': 'M',
            'l': 'L',
        }
        
        # Маппинг материалов корпуса
        self.case_materials = {
            'al': 'Aluminum',
            'aluminum': 'Aluminum',
            'ti': 'Titanium',
            'titanium': 'Titanium',
            'ss': 'Stainless Steel',
            'stainless steel': 'Stainless Steel',
        }
    
    def parse(self, text: str) -> list:
        """Парсит текст и извлекает данные Apple Watch"""
        results = []
        text_lower = text.lower()
        seen_combinations = set()  # Для отслеживания уникальных комбинаций
        
        # Проверяем, есть ли упоминание Apple Watch
        if not any(keyword in text_lower for keyword in ['apple watch', 'aw ', 'watch']):
            return results
        
        for pattern in self.patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                try:
                    watch_data = self._extract_watch_data(match, pattern)
                    if watch_data:
                        # Создаем уникальный ключ для проверки дублирования
                        key = (
                            watch_data.get('series', ''),
                            watch_data.get('size', ''),
                            watch_data.get('case_color', ''),
                            watch_data.get('band_type', ''),
                            watch_data.get('band_color', ''),
                            watch_data.get('band_size', ''),
                            watch_data.get('price', 0)
                        )
                        if key not in seen_combinations:
                            results.append(watch_data)
                            seen_combinations.add(key)
                except Exception as e:
                    logger.error(f"Ошибка парсинга Apple Watch: {e}")
                    continue
        
        return results
    
    def parse_lines(self, lines: list) -> tuple:
        """Парсит список строк и возвращает (parsed_data, unparsed_lines)"""
        parsed_data = []
        unparsed_lines = []
        processed_lines = set()  # Для отслеживания обработанных строк
        
        for line in lines:
            line = line.strip()
            if not line or line in processed_lines:
                continue
                
            results = self.parse(line)
            if results:
                parsed_data.extend(results)
                processed_lines.add(line)
            else:
                unparsed_lines.append(line)
        
        return parsed_data, unparsed_lines
    
    def _extract_watch_data(self, match, pattern: str) -> dict:
        """Извлекает данные Apple Watch из совпадения"""
        groups = match.groups()
        text = match.group(0)
        
        # Базовые поля
        series = ""
        size = ""
        case_color = ""
        band_type = ""
        band_color = ""
        band_size = ""
        product_code = ""
        country = "🇺🇸"  # По умолчанию
        price = 0
        
        try:
            # Определяем серию по паттерну
            if 'se' in pattern.lower():
                series = "SE"
            elif 'ultra' in pattern.lower():
                series = "Ultra 2"
            elif 'aw' in pattern.lower():
                # AW 10, AW 9 и т.д. - извлекаем из первой группы
                if len(groups) > 0 and groups[0].isdigit():
                    series = f"S{groups[0]}"
            elif 's' in pattern.lower() and any(char.isdigit() for char in pattern):
                # Извлекаем номер серии из паттерна
                series_match = re.search(r's(\d+)', pattern.lower())
                if series_match:
                    series = f"S{series_match.group(1)}"
            
            # Простая обработка групп
            if len(groups) >= 3:
                # Определяем размер и цвет в зависимости от паттерна
                if 'aw\\s+(\\d+)\\s+(\\d+)' in pattern and 'mm' not in pattern:
                    # AW 10 42 Rose Gold - первая группа серия, вторая размер
                    if len(groups) > 1 and groups[1].isdigit():
                        size = groups[1]
                    if len(groups) > 2:
                        case_color = self._normalize_case_color(groups[2])
                elif 'aw\\s+(\\d+)\\s+(\\d+)mm' in pattern:
                    # AW 10 46mm Silver - первая группа серия, вторая размер
                    if len(groups) > 1 and groups[1].isdigit():
                        size = groups[1]
                    if len(groups) > 2:
                        case_color = self._normalize_case_color(groups[2])
                elif 'aw\\s+ultra\\s+(\\d+)\\s+(\\d+)' in pattern:
                    # AW Ultra 2 49 - первая группа серия, вторая размер
                    if len(groups) > 1 and groups[1].isdigit():
                        size = groups[1]
                    if len(groups) > 2:
                        case_color = self._normalize_case_color(groups[2])
                else:
                    # Старая логика для других паттернов
                    if groups[0].isdigit():
                        size = groups[0]
                    elif len(groups) > 1 and groups[1].isdigit():
                        size = groups[1]
                    
                    if len(groups) > 1:
                        case_color = self._normalize_case_color(groups[1])
                    elif len(groups) > 2:
                        case_color = self._normalize_case_color(groups[2])
                
                # Последняя группа - цена
                for group in reversed(groups):
                    if group and re.match(r'[\d.,]+', str(group)):
                        price = self._parse_price(group)
                        break
                
                # Ищем код продукта
                for group in groups:
                    if group and re.match(r'^[A-Z0-9]{5,6}$', str(group)):
                        product_code = group
                        break
            
            # Проверяем наличие флага страны в тексте
            country_match = re.search(r'([🇺🇸🇯🇵🇮🇳🇪🇺🇦🇪🇨🇦🇻🇳]+)', text)
            if country_match:
                country = country_match.group(1)
            
            # Улучшенный парсинг ремешка из текста
            if 'sport band' in text.lower() or 'sb' in text.lower():
                band_type = 'Sport Band'
            elif 'sport loop' in text.lower() or 'sl' in text.lower():
                band_type = 'Sport Loop'
            elif 'milanese' in text.lower():
                band_type = 'Milanese Loop'
            elif 'ocean band' in text.lower():
                band_type = 'Ocean Band'
            elif 'alpine loop' in text.lower():
                band_type = 'Alpine Loop'
            elif 'trail' in text.lower():
                band_type = 'Trail Loop'
            
            # Парсим цвет ремешка
            if 'midnight' in text.lower() and 'midnight' not in case_color.lower():
                band_color = 'Midnight'
            elif 'silver' in text.lower() and 'silver' not in case_color.lower():
                band_color = 'Silver'
            elif 'rose gold' in text.lower() and 'rose gold' not in case_color.lower():
                band_color = 'Rose Gold'
            elif 'gold' in text.lower() and 'gold' not in case_color.lower():
                band_color = 'Gold'
            elif 'natural' in text.lower() and 'natural' not in case_color.lower():
                band_color = 'Natural'
            elif 'black' in text.lower() and 'black' not in case_color.lower():
                band_color = 'Black'
            elif 'blue' in text.lower() and 'blue' not in case_color.lower():
                band_color = 'Blue'
            elif 'indigo' in text.lower():
                band_color = 'Indigo'
            elif 'dark green' in text.lower():
                band_color = 'Dark Green'
            elif 'navi' in text.lower() or 'navy' in text.lower():
                band_color = 'Navy'
            
            # Парсим размер ремешка
            if 's/m' in text.lower():
                band_size = 'S/M'
            elif 'm/l' in text.lower():
                band_size = 'M/L'
            elif re.search(r'\b(s|m|l)\b', text.lower()):
                size_match = re.search(r'\b(s|m|l)\b', text.lower())
                if size_match:
                    band_size = size_match.group(1).upper()
            
            if not series or not size or not case_color or price <= 0:
                return None
            
            return {
                'firm': 'Apple',
                'device': 'Apple Watch',
                'series': series,
                'size': size,
                'case_color': case_color,
                'band_type': band_type,
                'band_color': band_color,
                'band_size': band_size,
                'product_code': product_code,
                'country': country,
                'price': price,
                'source_line': text
            }
        except Exception as e:
            logger.error(f"Ошибка извлечения данных Apple Watch: {e}")
            return None
    
    def _normalize_case_color(self, color: str) -> str:
        """Нормализует цвет корпуса"""
        color_lower = color.lower().strip()
        return self.case_colors.get(color_lower, color.title())
    
    def _normalize_band_type(self, band_type: str) -> str:
        """Нормализует тип ремешка"""
        band_lower = band_type.lower().strip()
        return self.band_types.get(band_lower, band_type.title())
    
    def _normalize_band_color(self, color: str) -> str:
        """Нормализует цвет ремешка"""
        color_lower = color.lower().strip()
        return self.band_colors.get(color_lower, color.title())
    
    def _parse_price(self, price_str: str) -> float:
        """Парсит цену из строки"""
        try:
            # Убираем все кроме цифр, точек и запятых
            price_clean = re.sub(r'[^\d.,]', '', str(price_str))
            # Заменяем запятую на точку
            price_clean = price_clean.replace(',', '.')
            return float(price_clean)
        except:
            return 0.0

# Создаем глобальный экземпляр
apple_watch_parser = AppleWatchParser()
