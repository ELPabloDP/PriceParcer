"""
Простой сервис для работы с iPhone
"""
import logging
from typing import List, Dict, Any, Optional
from decimal import Decimal
import os
import django
from django.conf import settings
from asgiref.sync import sync_to_async

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'db_app.settings')
django.setup()

from db_app.models import IPhone
from parsers.iphone_parser import IPhonePriceData, iphone_parser

logger = logging.getLogger(__name__)

class IPhoneServiceSimple:
    """Простой сервис для работы с iPhone"""
    
    async def parse_and_save_prices(self, text: str, source: str = "") -> Dict[str, Any]:
        """Парсит и сохраняет цены iPhone"""
        lines = text.split('\n')
        
        # Парсим с помощью шаблонов
        parsed_data, unparsed_lines = iphone_parser.parse_lines(lines)
        
        # Сохраняем распарсенные данные
        saved_count = 0
        for data in parsed_data:
            try:
                if await self._save_iphone_price(data, source):
                    saved_count += 1
            except Exception as e:
                logger.error(f"Ошибка сохранения цены iPhone: {e}")
        
        return {
            'template_parsed': len(parsed_data),
            'template_saved': saved_count,
            'gpt_parsed': len(unparsed_lines),
            'gpt_saved': 0,
            'total_saved': saved_count,
            'unparsed_lines': unparsed_lines
        }
    
    @sync_to_async
    def _save_iphone_price(self, data: IPhonePriceData, source: str) -> bool:
        """Сохраняет цену iPhone в БД"""
        try:
            # Создаем или обновляем iPhone запись
            iphone, created = IPhone.objects.update_or_create(
                generation=data.generation,
                variant=data.variant or None,
                storage=data.storage,
                color=data.color,
                country=data.country_flag,
                country_code=data.country_code or None,
                defaults={
                    'price': Decimal(data.price),
                    'source': source
                }
            )
            
            if created:
                logger.info(f"Создана новая цена iPhone: {iphone}")
            else:
                logger.info(f"Обновлена цена iPhone: {iphone}")
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка сохранения iPhone цены: {e}")
            return False
    
    @sync_to_async
    def get_catalog_data(self) -> Dict[str, Any]:
        """Получает данные каталога iPhone по поколениям"""
        try:
            catalog = {}
            
            # Получаем все поколения
            generations = IPhone.objects.values_list('generation', flat=True).distinct().order_by('generation')
            
            for generation in generations:
                # Получаем все iPhone этого поколения
                iphones = IPhone.objects.filter(generation=generation).order_by('variant', 'storage', 'color', 'country')
                
                generation_data = []
                for iphone in iphones:
                    generation_data.append({
                        'id': iphone.id,
                        'name': iphone.full_name,
                        'price': int(iphone.price),
                        'display_price': iphone.display_price,
                        'country': iphone.country,
                        'variant': iphone.variant_display,
                        'storage': iphone.storage,
                        'color': iphone.color
                    })
                
                if generation_data:
                    catalog[f"iPhone {generation}"] = generation_data
            
            return catalog
            
        except Exception as e:
            logger.error(f"Ошибка получения каталога iPhone: {e}")
            return {}
    
    @sync_to_async
    def clear_all_data(self) -> int:
        """Очищает все данные iPhone"""
        try:
            count = IPhone.objects.count()
            IPhone.objects.all().delete()
            logger.info(f"Очищены данные iPhone: {count} записей")
            return count
        except Exception as e:
            logger.error(f"Ошибка очистки данных iPhone: {e}")
            return 0

# Создаем глобальный экземпляр сервиса
iphone_service_simple = IPhoneServiceSimple()
