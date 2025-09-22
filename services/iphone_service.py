"""
Сервис для работы с iPhone данными
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

from db_app.iphone_models import (
    IPhoneGeneration, IPhoneVariant, IPhoneStorage, 
    IPhoneColor, IPhoneCountry, IPhonePrice, IPhoneBestPrice
)
from parsers.iphone_parser import IPhonePriceData, iphone_parser

logger = logging.getLogger(__name__)

class IPhoneService:
    """Сервис для работы с iPhone"""
    
    def __init__(self):
        pass  # Инициализация будет вызвана асинхронно
    
    @sync_to_async
    def _init_default_data(self):
        """Инициализирует базовые данные"""
        # Поколения
        generations = [
            ('11', 'iPhone 11'),
            ('12', 'iPhone 12'), 
            ('13', 'iPhone 13'),
            ('14', 'iPhone 14'),
            ('15', 'iPhone 15'),
            ('16', 'iPhone 16'),
            ('16E', 'iPhone 16E'),
        ]
        for number, display_name in generations:
            IPhoneGeneration.objects.get_or_create(
                number=number,
                defaults={'display_name': display_name}
            )
        
        # Варианты
        variants = [
            ('', 'iPhone', 0),
            ('Plus', 'iPhone Plus', 1),
            ('Pro', 'iPhone Pro', 2), 
            ('Pro Max', 'iPhone Pro Max', 3),
        ]
        for name, display_name, sort_order in variants:
            IPhoneVariant.objects.get_or_create(
                name=name,
                defaults={'display_name': display_name, 'sort_order': sort_order}
            )
        
        # Объемы памяти
        storages = [
            ('64GB', 64),
            ('128GB', 128),
            ('256GB', 256),
            ('512GB', 512),
            ('1TB', 1024),
        ]
        for capacity, size_gb in storages:
            IPhoneStorage.objects.get_or_create(
                capacity=capacity,
                defaults={'size_gb': size_gb}
            )
        
        # Базовые цвета
        colors = [
            ('Black', 'Черный'),
            ('White', 'Белый'),
            ('Blue', 'Синий'),
            ('Green', 'Зеленый'),
            ('Red', 'Красный'),
            ('Pink', 'Розовый'),
            ('Purple', 'Фиолетовый'),
            ('Yellow', 'Желтый'),
            ('Midnight', 'Темная ночь'),
            ('Starlight', 'Сияющая звезда'),
            ('Natural', 'Натуральный'),
            ('Desert', 'Пустыня'),
            ('Ultramarine', 'Ультрамарин'),
            ('Teal', 'Бирюзовый'),
            ('Titanium', 'Титан'),
        ]
        for name, display_name in colors:
            IPhoneColor.objects.get_or_create(
                name=name,
                defaults={'display_name': display_name}
            )
        
        # Страны
        countries = [
            ('🇺🇸', 'США', ''),
            ('🇯🇵', 'Япония', ''),
            ('🇮🇳', 'Индия', ''),
            ('🇨🇳', 'Китай', ''),
            ('🇦🇪', 'ОАЭ', ''),
            ('🇭🇰', 'Гонконг', ''),
            ('🇰🇷', 'Южная Корея', ''),
            ('🇪🇺', 'Европа', ''),
            ('🇷🇺', 'Россия', ''),
            ('🇨🇦', 'Канада', ''),
            ('🇻🇳', 'Вьетнам', ''),
            ('🇨🇳', 'Китай 2SIM', '2SIM'),
        ]
        for flag, name, code in countries:
            IPhoneCountry.objects.get_or_create(
                flag=flag,
                code=code,
                defaults={'name': name}
            )
    
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
        
        # Если есть нераспознанные строки, отправляем их в GPT
        gpt_saved = 0
        if unparsed_lines:
            logger.info(f"Отправляем {len(unparsed_lines)} нераспознанных строк в GPT")
            # TODO: Интеграция с GPT для нераспознанных строк
        
        return {
            'template_parsed': len(parsed_data),
            'template_saved': saved_count,
            'gpt_parsed': len(unparsed_lines),
            'gpt_saved': gpt_saved,
            'total_saved': saved_count + gpt_saved,
            'unparsed_lines': unparsed_lines
        }
    
    @sync_to_async
    def _save_iphone_price(self, data: IPhonePriceData, source: str) -> bool:
        """Сохраняет цену iPhone в БД"""
        try:
            # Получаем или создаем связанные объекты
            generation, _ = IPhoneGeneration.objects.get_or_create(
                number=data.generation,
                defaults={'display_name': f'iPhone {data.generation}'}
            )
            
            variant, _ = IPhoneVariant.objects.get_or_create(
                name=data.variant,
                defaults={
                    'display_name': f'iPhone {data.variant}' if data.variant else 'iPhone',
                    'sort_order': {'': 0, 'Plus': 1, 'Pro': 2, 'Pro Max': 3}.get(data.variant, 99)
                }
            )
            
            storage, _ = IPhoneStorage.objects.get_or_create(
                capacity=data.storage,
                defaults={'size_gb': int(data.storage.replace('GB', '').replace('TB', '')) * (1024 if 'TB' in data.storage else 1)}
            )
            
            color, _ = IPhoneColor.objects.get_or_create(
                name=data.color,
                defaults={'display_name': data.color}
            )
            
            country, _ = IPhoneCountry.objects.get_or_create(
                flag=data.country_flag,
                code=data.country_code,
                defaults={'name': 'Неизвестная страна'}
            )
            
            # Создаем или обновляем цену
            price_obj, created = IPhonePrice.objects.update_or_create(
                generation=generation,
                variant=variant,
                storage=storage,
                color=color,
                country=country,
                defaults={
                    'price': Decimal(data.price),
                    'source': source
                }
            )
            
            # Обновляем лучшую цену
            self._update_best_price(generation, variant, storage, color)
            
            if created:
                logger.info(f"Создана новая цена iPhone: {price_obj}")
            else:
                logger.info(f"Обновлена цена iPhone: {price_obj}")
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка сохранения iPhone цены: {e}")
            return False
    
    def _update_best_price(self, generation, variant, storage, color):
        """Обновляет лучшую цену для конкретной конфигурации"""
        try:
            # Находим самую дешевую цену для этой конфигурации
            best_price = IPhonePrice.objects.filter(
                generation=generation,
                variant=variant,
                storage=storage,
                color=color
            ).order_by('price').first()
            
            if best_price:
                IPhoneBestPrice.objects.update_or_create(
                    generation=generation,
                    variant=variant,
                    storage=storage,
                    color=color,
                    defaults={'best_price': best_price}
                )
                
        except Exception as e:
            logger.error(f"Ошибка обновления лучшей цены: {e}")
    
    @sync_to_async
    def get_catalog_data(self) -> Dict[str, Any]:
        """Получает данные каталога iPhone"""
        try:
            catalog = {}
            
            # Группируем по поколениям
            for generation in IPhoneGeneration.objects.all().order_by('number'):
                generation_data = {}
                
                # Группируем по вариантам
                for variant in IPhoneVariant.objects.all().order_by('sort_order'):
                    best_prices = IPhoneBestPrice.objects.filter(
                        generation=generation,
                        variant=variant
                    ).select_related('best_price', 'storage', 'color').order_by(
                        'storage__size_gb', 'color__name'
                    )
                    
                    if best_prices.exists():
                        variant_data = []
                        for bp in best_prices:
                            variant_data.append({
                                'id': bp.best_price.id,
                                'name': bp.best_price.full_name,
                                'price': int(bp.best_price.price),
                                'display_price': bp.best_price.display_price,
                                'country': bp.best_price.country.flag,
                                'storage': bp.storage.capacity,
                                'color': bp.color.display_name
                            })
                        
                        variant_key = variant.display_name if variant.name else f"iPhone {generation.number}"
                        generation_data[variant_key] = variant_data
                
                if generation_data:
                    catalog[generation.display_name] = generation_data
            
            return catalog
            
        except Exception as e:
            logger.error(f"Ошибка получения каталога iPhone: {e}")
            return {}
    
    @sync_to_async
    def clear_all_data(self) -> int:
        """Очищает все данные iPhone"""
        try:
            count = IPhonePrice.objects.count()
            IPhonePrice.objects.all().delete()
            IPhoneBestPrice.objects.all().delete()
            logger.info(f"Очищены данные iPhone: {count} записей")
            return count
        except Exception as e:
            logger.error(f"Ошибка очистки данных iPhone: {e}")
            return 0

# Создаем глобальный экземпляр сервиса
iphone_service = IPhoneService()
