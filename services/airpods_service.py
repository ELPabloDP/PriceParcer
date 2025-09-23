"""
Сервис для работы с AirPods
"""
import logging
from typing import List, Dict, Any
from django.utils import timezone
from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)

class AirPodsService:
    """Сервис для сохранения данных AirPods"""
    
    @sync_to_async
    def save_airpods_price(self, airpods_data: Dict[str, Any]) -> bool:
        """Сохраняет цену AirPods в базу данных"""
        try:
            from db_app.models import AirPods
            
            # Создаем или обновляем запись
            airpods, created = AirPods.objects.update_or_create(
                model=airpods_data.get('variant', 'AirPods'),
                generation=airpods_data.get('generation', '4'),
                features=airpods_data.get('features', ''),
                color=airpods_data.get('color', 'White'),
                year=airpods_data.get('year', ''),
                country=airpods_data.get('country', '🇺🇸'),
                defaults={
                    'price': airpods_data.get('price', 0),
                    'product_code': airpods_data.get('product_code', ''),
                    'source': f"Parsed at {timezone.now()}",
                }
            )
            
            action = "создана" if created else "обновлена"
            logger.info(f"AirPods запись {action}: {airpods}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка сохранения AirPods: {e}")
            return False
    
    @sync_to_async
    def get_all_airpods(self) -> List[Dict[str, Any]]:
        """Получает все AirPods из базы данных"""
        try:
            from db_app.models import AirPods
            
            airpods = AirPods.objects.all().order_by('model', 'generation', 'features')
            
            return [
                {
                    'id': ap.id,
                    'model': ap.model,
                    'generation': ap.generation,
                    'features': ap.features,
                    'color': ap.color,
                    'year': ap.year,
                    'country': ap.country,
                    'price': int(ap.display_price),
                    'product_code': ap.product_code,
                    'full_name': ap.full_name,
                    'model_display': ap.model_display,
                }
                for ap in airpods
            ]
            
        except Exception as e:
            logger.error(f"Ошибка получения AirPods: {e}")
            return []
    
    @sync_to_async
    def get_airpods_by_model(self, model: str) -> List[Dict[str, Any]]:
        """Получает AirPods по модели"""
        try:
            from db_app.models import AirPods
            
            airpods = AirPods.objects.filter(model__icontains=model).order_by('generation', 'features')
            
            return [
                {
                    'id': ap.id,
                    'model': ap.model,
                    'generation': ap.generation,
                    'features': ap.features,
                    'color': ap.color,
                    'year': ap.year,
                    'country': ap.country,
                    'price': int(ap.display_price),
                    'product_code': ap.product_code,
                    'full_name': ap.full_name,
                }
                for ap in airpods
            ]
            
        except Exception as e:
            logger.error(f"Ошибка получения AirPods по модели {model}: {e}")
            return []
