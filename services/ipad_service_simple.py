"""
Простой сервис для работы с iPad
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

from db_app.models import iPad, Markup

logger = logging.getLogger(__name__)

class iPadServiceSimple:
    def __init__(self):
        pass

    @sync_to_async
    def save_ipad_price(self, price_data: Dict[str, Any]) -> Optional[iPad]:
        """Сохраняет цену iPad"""
        try:
            # Извлекаем данные из price_data
            generation = price_data.get('generation', '')
            variant = price_data.get('variant', '')
            size = price_data.get('size', '')
            storage = price_data.get('storage', '')
            color = price_data.get('color', '')
            connectivity = price_data.get('connectivity', '')
            product_code = price_data.get('product_code', '')
            country = price_data.get('country', '')
            price = price_data.get('price', 0)
            source = price_data.get('source', '')

            if not price or price <= 0:
                logger.warning(f"Некорректная цена для iPad: {price_data}")
                return None

            # Исправляем неправильные данные от GPT
            if generation and ' ' in generation:
                # Если generation содержит пробелы (например "Air 11", "Pro 13"), исправляем
                parts = generation.split()
                if len(parts) >= 2:
                    if parts[0] in ['Air', 'Pro', 'Mini']:
                        variant = parts[0]
                        size = parts[1]
                        generation = parts[2] if len(parts) > 2 else ''
                    else:
                        generation = parts[0]
                        if len(parts) > 1:
                            size = parts[1]
            
            # Дополнительная проверка для исправления неправильных данных
            if generation and generation in ['Air', 'Pro', 'Mini']:
                # Если generation содержит только "Air", "Pro" или "Mini", это неправильно
                if not variant:
                    variant = generation
                    generation = ''
            
            # Исправляем дублирование в generation
            if generation and ' ' in generation:
                parts = generation.split()
                if len(parts) > 1 and parts[0] == parts[1]:
                    generation = parts[0]

            # Создаем или обновляем запись
            ipad, created = iPad.objects.update_or_create(
                generation=generation,
                variant=variant,
                size=size,
                storage=storage,
                color=color,
                connectivity=connectivity,
                country=country,
                defaults={
                    'product_code': product_code,
                    'price': Decimal(price),
                    'source': source
                }
            )

            if created:
                logger.info(f"Создан новый iPad: {ipad.full_name} - {price}₽")
            else:
                logger.info(f"Обновлен iPad: {ipad.full_name} - {price}₽")

            return ipad

        except Exception as e:
            logger.error(f"Ошибка сохранения iPad: {e}")
            return None

    @sync_to_async
    def parse_and_save_prices(self, text: str, source: str = "") -> Dict[str, int]:
        """Парсит и сохраняет цены iPad из текста"""
        try:
            from parsers.ipad_parser import iPadParser
            
            lines = text.strip().split('\n')
            parser = iPadParser()
            parsed_data, unparsed_lines = parser.parse_lines(lines)
            
            saved_count = 0
            for data in parsed_data:
                price_data = data.to_dict()
                price_data['source'] = source
                result = self.save_ipad_price(price_data)
                if result:
                    saved_count += 1
            
            return {
                'parsed': len(parsed_data),
                'saved': saved_count,
                'unparsed': len(unparsed_lines)
            }
            
        except Exception as e:
            logger.error(f"Ошибка парсинга iPad: {e}")
            return {
                'parsed': 0,
                'saved': 0,
                'unparsed': 0
            }

# Создаем экземпляр сервиса
ipad_service_simple = iPadServiceSimple()


