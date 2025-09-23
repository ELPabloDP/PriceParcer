"""
Сервис для работы с Apple Pencil
"""
import logging
from typing import List, Dict, Any
from django.utils import timezone
from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)

class ApplePencilService:
    """Сервис для сохранения данных Apple Pencil"""
    
    @sync_to_async
    def save_apple_pencil_price(self, pencil_data: Dict[str, Any]) -> bool:
        """Сохраняет цену Apple Pencil в базу данных"""
        try:
            from db_app.models import ApplePencil
            
            # Создаем или обновляем запись
            pencil, created = ApplePencil.objects.update_or_create(
                model=pencil_data.get('variant', 'Apple Pencil'),
                generation=pencil_data.get('generation', '2'),
                connector=pencil_data.get('connector', 'Lightning'),
                country=pencil_data.get('country', '🇺🇸'),
                defaults={
                    'price': pencil_data.get('price', 0),
                    'product_code': pencil_data.get('product_code', ''),
                    'source': f"Parsed at {timezone.now()}",
                }
            )
            
            action = "создана" if created else "обновлена"
            logger.info(f"Apple Pencil запись {action}: {pencil}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка сохранения Apple Pencil: {e}")
            return False
    
    @sync_to_async
    def get_all_apple_pencils(self) -> List[Dict[str, Any]]:
        """Получает все Apple Pencil из базы данных"""
        try:
            from db_app.models import ApplePencil
            
            pencils = ApplePencil.objects.all().order_by('generation', 'connector')
            
            return [
                {
                    'id': pencil.id,
                    'model': pencil.model,
                    'generation': pencil.generation,
                    'connector': pencil.connector,
                    'country': pencil.country,
                    'price': int(pencil.display_price),
                    'product_code': pencil.product_code,
                    'full_name': pencil.full_name,
                    'model_display': pencil.model_display,
                }
                for pencil in pencils
            ]
            
        except Exception as e:
            logger.error(f"Ошибка получения Apple Pencil: {e}")
            return []
