"""
Сервис для работы с Apple Watch
"""
import logging
from typing import List, Dict, Any
from django.utils import timezone
from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)

class AppleWatchService:
    """Сервис для сохранения данных Apple Watch"""
    
    @sync_to_async
    def save_apple_watch_price(self, watch_data: Dict[str, Any]) -> bool:
        """Сохраняет цену Apple Watch в базу данных"""
        try:
            from db_app.models import AppleWatch
            
            # Создаем или обновляем запись
            watch, created = AppleWatch.objects.update_or_create(
                series=watch_data.get('variant', 'SE'),
                size=watch_data.get('size', '40'),
                case_color=watch_data.get('color', 'Midnight'),
                band_type=watch_data.get('band_type', 'Sport Band'),
                band_color=watch_data.get('band_color', ''),
                band_size=watch_data.get('band_size', 'M/L'),
                connectivity=watch_data.get('connectivity', 'GPS'),
                country=watch_data.get('country', '🇺🇸'),
                defaults={
                    'case_material': watch_data.get('case_material', 'Aluminum'),
                    'price': watch_data.get('price', 0),
                    'product_code': watch_data.get('product_code', ''),
                    'source': f"Parsed at {timezone.now()}",
                }
            )
            
            action = "создана" if created else "обновлена"
            logger.info(f"Apple Watch запись {action}: {watch}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка сохранения Apple Watch: {e}")
            return False
    
    @sync_to_async
    def get_all_apple_watches(self) -> List[Dict[str, Any]]:
        """Получает все Apple Watch из базы данных"""
        try:
            from db_app.models import AppleWatch
            
            watches = AppleWatch.objects.all().order_by('series', 'size', 'case_color')
            
            return [
                {
                    'id': watch.id,
                    'series': watch.series,
                    'size': watch.size,
                    'case_material': watch.case_material,
                    'case_color': watch.case_color,
                    'band_type': watch.band_type,
                    'band_color': watch.band_color,
                    'band_size': watch.band_size,
                    'connectivity': watch.connectivity,
                    'country': watch.country,
                    'price': int(watch.display_price),
                    'product_code': watch.product_code,
                    'full_name': watch.full_name,
                    'series_display': watch.series_display,
                    'size_display': watch.size_display,
                }
                for watch in watches
            ]
            
        except Exception as e:
            logger.error(f"Ошибка получения Apple Watch: {e}")
            return []
    
    @sync_to_async
    def get_watches_by_series(self, series: str) -> List[Dict[str, Any]]:
        """Получает Apple Watch по серии"""
        try:
            from db_app.models import AppleWatch
            
            watches = AppleWatch.objects.filter(series=series).order_by('size', 'case_color')
            
            return [
                {
                    'id': watch.id,
                    'series': watch.series,
                    'size': watch.size,
                    'case_material': watch.case_material,
                    'case_color': watch.case_color,
                    'band_type': watch.band_type,
                    'band_color': watch.band_color,
                    'band_size': watch.band_size,
                    'connectivity': watch.connectivity,
                    'country': watch.country,
                    'price': int(watch.display_price),
                    'product_code': watch.product_code,
                    'full_name': watch.full_name,
                }
                for watch in watches
            ]
            
        except Exception as e:
            logger.error(f"Ошибка получения Apple Watch по серии {series}: {e}")
            return []
