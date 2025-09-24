"""
Сервис для работы с iMac
"""
import logging
from typing import List, Dict, Any
from django.utils import timezone
from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)

class iMacService:
    """Сервис для сохранения данных iMac"""
    
    async def parse_and_save_prices(self, lines: list, source: str = "") -> tuple[list, int]:
        """
        Парсит строки и сохраняет цены
        Возвращает (parsed_items, saved_count)
        """
        from parsers.imac_parser import iMacParser
        
        parser = iMacParser()
        parsed_items, unparsed = parser.parse_lines(lines)
        
        saved_count = 0
        for item in parsed_items:
            # Конвертируем в формат для save_imac_price
            data = {
                'device': 'iMac',
                'generation': item.chip,
                'variant': item.size,
                'memory': item.memory,
                'storage': item.storage,
                'color': item.color,
                'country': item.country,
                'price': str(item.price),
                'product_code': item.product_code,
                'source': source
            }
            
            if await self.save_imac_price(data):
                saved_count += 1
        
        return parsed_items, saved_count
    
    @sync_to_async
    def save_imac_price(self, imac_data: Dict[str, Any]) -> bool:
        """Сохраняет цену iMac в базу данных"""
        try:
            from db_app.models import iMac
            
            # Создаем или обновляем запись
            imac, created = iMac.objects.update_or_create(
                model=imac_data.get('device', 'iMac'),
                chip=imac_data.get('generation', 'M1'),
                size=imac_data.get('variant', '24'),
                memory=imac_data.get('memory', '8GB'),
                storage=imac_data.get('storage', '256GB'),
                color=imac_data.get('color', 'Silver'),
                country=imac_data.get('country', '🇺🇸'),
                defaults={
                    'price': imac_data.get('price', 0),
                    'product_code': imac_data.get('product_code', ''),
                    'source': f"Parsed at {timezone.now()}",
                }
            )
            
            action = "создана" if created else "обновлена"
            logger.info(f"iMac запись {action}: {imac}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка сохранения iMac: {e}")
            return False
    
    @sync_to_async
    def get_all_imacs(self) -> List[Dict[str, Any]]:
        """Получает все iMac из базы данных"""
        try:
            from db_app.models import iMac
            
            imacs = iMac.objects.all().order_by('model', 'chip', 'size')
            
            return [
                {
                    'id': imac.id,
                    'model': imac.model,
                    'chip': imac.chip,
                    'size': imac.size,
                    'memory': imac.memory,
                    'storage': imac.storage,
                    'color': imac.color,
                    'country': imac.country,
                    'price': int(imac.display_price),
                    'product_code': imac.product_code,
                    'full_name': imac.full_name,
                    'model_display': imac.model_display,
                }
                for imac in imacs
            ]
            
        except Exception as e:
            logger.error(f"Ошибка получения iMac: {e}")
            return []
    
    @sync_to_async
    def get_imacs_by_model(self, model: str) -> List[Dict[str, Any]]:
        """Получает iMac по модели"""
        try:
            from db_app.models import iMac
            
            imacs = iMac.objects.filter(model=model).order_by('chip', 'size')
            
            return [
                {
                    'id': imac.id,
                    'model': imac.model,
                    'chip': imac.chip,
                    'size': imac.size,
                    'memory': imac.memory,
                    'storage': imac.storage,
                    'color': imac.color,
                    'country': imac.country,
                    'price': int(imac.display_price),
                    'product_code': imac.product_code,
                    'full_name': imac.full_name,
                }
                for imac in imacs
            ]
            
        except Exception as e:
            logger.error(f"Ошибка получения iMac по модели {model}: {e}")
            return []
