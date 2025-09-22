import logging
from typing import Dict, Any, Optional
from asgiref.sync import sync_to_async
from db_app.models import AppleWatch

logger = logging.getLogger(__name__)

class AppleWatchServiceSimple:
    """Сервис для работы с Apple Watch"""
    
    def __init__(self):
        pass
    
    async def parse_and_save_prices(self, text: str, source: str = "") -> Dict[str, Any]:
        """Парсит и сохраняет цены Apple Watch"""
        lines = text.split('\n')
        
        # Парсим с помощью шаблонов
        from parsers.apple_watch_parser import apple_watch_parser
        parsed_data, unparsed_lines = apple_watch_parser.parse_lines(lines)
        
        # Сохраняем распарсенные данные
        saved_count = 0
        for data in parsed_data:
            try:
                if await self.save_apple_watch_price(data):
                    saved_count += 1
            except Exception as e:
                logger.error(f"Ошибка сохранения цены Apple Watch: {e}")
        
        return {
            'template_parsed': len(parsed_data),
            'template_saved': saved_count,
            'gpt_parsed': len(unparsed_lines),
            'gpt_saved': 0,
            'total_saved': saved_count,
            'unparsed_lines': unparsed_lines
        }
    
    @sync_to_async
    def save_apple_watch_price(self, price_data: Dict[str, Any]) -> Optional[AppleWatch]:
        """Сохраняет цену Apple Watch в базу данных"""
        try:
            # Извлекаем данные
            series = price_data.get('series', '')
            size = price_data.get('size', '')
            case_color = price_data.get('case_color', '')
            band_type = price_data.get('band_type', '')
            band_color = price_data.get('band_color', '')
            band_size = price_data.get('band_size', '')
            connectivity = price_data.get('connectivity', '')
            product_code = price_data.get('product_code', '')
            country = price_data.get('country', '🇺🇸')
            price = price_data.get('price', 0)
            source = price_data.get('source', '')
            
            # Валидация обязательных полей
            if not series or not size or not case_color or price <= 0:
                logger.warning(f"Недостаточно данных для Apple Watch: {price_data}")
                return None
            
            # Нормализуем данные
            series = self._normalize_series(series)
            size = self._normalize_size(size)
            case_color = self._normalize_case_color(case_color)
            band_type = self._normalize_band_type(band_type) if band_type else ''
            band_color = self._normalize_band_color(band_color) if band_color else ''
            band_size = self._normalize_band_size(band_size) if band_size else ''
            connectivity = self._normalize_connectivity(connectivity) if connectivity else ''
            
            # Создаем или обновляем запись
            apple_watch, created = AppleWatch.objects.update_or_create(
                series=series,
                size=size,
                case_color=case_color,
                band_type=band_type,
                band_color=band_color,
                band_size=band_size,
                connectivity=connectivity,
                country=country,
                defaults={
                    'price': price,
                    'product_code': product_code,
                    'source': source
                }
            )
            
            action = "создана" if created else "обновлена"
            logger.info(f"Apple Watch {action}: {apple_watch.full_name} - {price}₽")
            return apple_watch
            
        except Exception as e:
            logger.error(f"Ошибка сохранения Apple Watch: {e}")
            return None
    
    def _normalize_series(self, series: str) -> str:
        """Нормализует серию Apple Watch"""
        series = series.strip().upper()
        
        # Маппинг серий
        series_mapping = {
            'SE': 'SE',
            'S10': 'S10',
            'S9': 'S9',
            'S8': 'S8',
            'S7': 'S7',
            'S6': 'S6',
            'S5': 'S5',
            'S4': 'S4',
            'S3': 'S3',
            'S2': 'S2',
            'S1': 'S1',
            'ULTRA 2': 'Ultra 2',
            'ULTRA': 'Ultra',
        }
        
        return series_mapping.get(series, series)
    
    def _normalize_size(self, size: str) -> str:
        """Нормализует размер Apple Watch"""
        size = str(size).strip()
        
        # Убираем 'mm' если есть
        if size.endswith('mm'):
            size = size[:-2]
        
        # Проверяем валидные размеры
        valid_sizes = ['38', '40', '41', '42', '44', '45', '46', '49']
        if size in valid_sizes:
            return size
        
        # Пытаемся извлечь число
        import re
        size_match = re.search(r'(\d+)', size)
        if size_match:
            size_num = size_match.group(1)
            if size_num in valid_sizes:
                return size_num
        
        return size
    
    def _normalize_case_color(self, color: str) -> str:
        """Нормализует цвет корпуса"""
        color = color.strip().title()
        
        # Маппинг цветов корпуса
        color_mapping = {
            'Midnight': 'Midnight',
            'Silver': 'Silver',
            'Starlight': 'Starlight',
            'Rose Gold': 'Rose Gold',
            'Jet Black': 'Jet Black',
            'Space Black': 'Space Black',
            'Natural Titanium': 'Natural Titanium',
            'Blue': 'Blue',
            'Green': 'Green',
            'Gray': 'Gray',
            'Grey': 'Gray',
            'Titanium': 'Titanium',
            'Orange': 'Orange',
            'Indigo': 'Indigo',
        }
        
        return color_mapping.get(color, color)
    
    def _normalize_band_type(self, band_type: str) -> str:
        """Нормализует тип ремешка"""
        band_type = band_type.strip().title()
        
        # Маппинг типов ремешков
        band_type_mapping = {
            'Sport Band': 'Sport Band',
            'Sport Loop': 'Sport Loop',
            'Milanese Loop': 'Milanese Loop',
            'Ocean Band': 'Ocean Band',
            'Alpine Loop': 'Alpine Loop',
            'Trail Loop': 'Trail Loop',
            'Leather Loop': 'Leather Loop',
            'Nike Sport Band': 'Nike Sport Band',
            'Nike Sport Loop': 'Nike Sport Loop',
        }
        
        return band_type_mapping.get(band_type, band_type)
    
    def _normalize_band_color(self, color: str) -> str:
        """Нормализует цвет ремешка"""
        color = color.strip().title()
        
        # Маппинг цветов ремешков
        color_mapping = {
            'Midnight': 'Midnight',
            'Silver': 'Silver',
            'Starlight': 'Starlight',
            'Lake Green': 'Lake Green',
            'Denim': 'Denim',
            'Blue': 'Blue',
            'Black': 'Black',
            'Dark Green': 'Dark Green',
            'Navy': 'Navy',
            'Orange': 'Orange',
            'Beige': 'Beige',
            'Indigo': 'Indigo',
            'Plum': 'Plum',
            'Blue Cloud': 'Blue Cloud',
            'Natural': 'Natural',
        }
        
        return color_mapping.get(color, color)
    
    def _normalize_band_size(self, size: str) -> str:
        """Нормализует размер ремешка"""
        size = size.strip().upper()
        
        # Маппинг размеров ремешков
        size_mapping = {
            'S/M': 'S/M',
            'M/L': 'M/L',
            'S': 'S',
            'M': 'M',
            'L': 'L',
        }
        
        return size_mapping.get(size, size)
    
    def _normalize_connectivity(self, connectivity: str) -> str:
        """Нормализует тип подключения"""
        connectivity = connectivity.strip().upper()
        
        # Маппинг типов подключения
        connectivity_mapping = {
            'GPS': 'GPS',
            'CELLULAR': 'Cellular',
            'GPS+CELLULAR': 'GPS+Cellular',
            'GPS+Cellular': 'GPS+Cellular',
        }
        
        return connectivity_mapping.get(connectivity, connectivity)

# Создаем глобальный экземпляр
apple_watch_service_simple = AppleWatchServiceSimple()
