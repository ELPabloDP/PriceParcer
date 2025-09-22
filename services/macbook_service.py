"""
Сервис для работы с MacBook
"""
import logging
from typing import List, Dict, Any, Optional
from decimal import Decimal
import os
import django
from django.conf import settings
from asgiref.sync import sync_to_async

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'db_app.settings')
django.setup()

from db_app.models import Product, Markup

logger = logging.getLogger(__name__)

class MacBookService:
    def __init__(self):
        pass

    @sync_to_async
    def save_macbook_price(self, price_data: Dict[str, Any]) -> Optional[Product]:
        """Сохраняет цену MacBook"""
        try:
            firm = price_data.get('firm', 'Apple')
            device = price_data.get('device', 'MacBook')
            generation = price_data.get('generation', '')
            variant = price_data.get('variant', '')
            configuration = price_data.get('configuration', '')
            product_code = price_data.get('product_code', '')
            country_flag = price_data.get('country', '🇺🇸')
            price = price_data.get('price')

            if not price or price <= 0:
                logger.warning(f"Некорректная цена для MacBook: {price_data}")
                return None

            product, created = Product.objects.update_or_create(
                firm=firm,
                device=device,
                generation=generation,
                variant=variant,
                configuration=configuration,
                country=country_flag,
                defaults={
                    'product_code': product_code,
                    'price': Decimal(price)
                }
            )

            if created:
                logger.info(f"Создан новый MacBook: {product.full_name} - {price}₽")
            else:
                logger.info(f"Обновлена цена MacBook: {product.full_name} - {price}₽")

            return product

        except Exception as e:
            logger.error(f"Ошибка сохранения MacBook: {e}")
            return None

    @sync_to_async
    def get_macbook_catalog(self) -> Dict[str, Any]:
        """Получает каталог MacBook"""
        try:
            # Получаем все MacBook
            macbooks = Product.objects.filter(
                firm='Apple',
                device='MacBook'
            ).order_by('variant', 'generation', 'configuration', 'country')
            
            catalog = {}
            
            for macbook in macbooks:
                variant = macbook.variant or 'Air'
                
                if variant not in catalog:
                    catalog[variant] = []
                
                # Формируем название с размером экрана
                name_parts = [f"MacBook {variant}"]
                if macbook.generation:
                    # Извлекаем размер экрана из конфигурации
                    import re
                    size_match = re.search(r'(\d+)\s*inch', macbook.configuration or '')
                    if size_match:
                        name_parts.append(f"{size_match.group(1)}")
                    else:
                        name_parts.append(macbook.generation)
                
                # Формируем конфигурацию с кодом продукта
                config_parts = []
                if macbook.configuration:
                    config_parts.append(macbook.configuration)
                if macbook.product_code:
                    config_parts.append(f"({macbook.product_code})")
                configuration = " ".join(config_parts)
                
                catalog[variant].append({
                    'id': macbook.id,
                    'name': " ".join(name_parts),
                    'configuration': configuration,
                    'price': int(macbook.price),
                    'display_price': macbook.display_price,
                    'country': macbook.country,
                    'product_code': macbook.product_code or '',
                    'generation': macbook.generation or ''
                })
            
            return catalog
        except Exception as e:
            logger.error(f"Ошибка получения каталога MacBook: {e}")
            return {}

macbook_service = MacBookService()
