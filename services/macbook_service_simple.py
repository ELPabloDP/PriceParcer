"""
Простой сервис для работы с MacBook
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

from db_app.models import MacBook, Markup

logger = logging.getLogger(__name__)

class MacBookServiceSimple:
    def __init__(self):
        pass

    @sync_to_async
    def save_macbook_price(self, price_data: Dict[str, Any]) -> Optional[MacBook]:
        """Сохраняет цену MacBook"""
        try:
            # Извлекаем данные из price_data
            generation = price_data.get('generation', '')
            variant = price_data.get('variant', '')
            size = price_data.get('size', '')
            memory = price_data.get('memory', '')
            storage = price_data.get('storage', '')
            color = price_data.get('color', '')
            configuration = price_data.get('configuration', '')
            product_code = price_data.get('product_code', '')
            country = price_data.get('country', '')
            price = price_data.get('price', 0)
            source = price_data.get('source', '')

            if not price or price <= 0:
                logger.warning(f"Некорректная цена для MacBook: {price_data}")
                return None

            # Исправляем неправильные данные от GPT
            if generation and ' ' in generation:
                # Если generation содержит пробелы (например "Air 13", "Pro 14"), исправляем
                parts = generation.split()
                if len(parts) >= 2:
                    if parts[0] in ['Air', 'Pro']:
                        variant = parts[0]
                        size = parts[1]
                        generation = parts[2] if len(parts) > 2 else ''
                    else:
                        generation = parts[0]
                        if len(parts) > 1:
                            size = parts[1]
            
            # Дополнительная проверка для исправления неправильных данных
            if generation and generation in ['Air', 'Pro']:
                # Если generation содержит только "Air" или "Pro", это неправильно
                if not variant:
                    variant = generation
                    generation = ''
            
            # Исправляем дублирование в generation
            if generation and ' ' in generation:
                parts = generation.split()
                if len(parts) > 1 and parts[0] == parts[1]:
                    generation = parts[0]

            # Парсим конфигурацию для извлечения memory, storage, color
            if configuration:
                memory_parsed, storage_parsed, color_parsed = self._parse_configuration(configuration)
                memory = memory or memory_parsed
                storage = storage or storage_parsed
                color = color or color_parsed

            # Исправляем дублирование памяти
            if memory and ' ' in memory:
                # Если memory содержит пробелы, берем только первое значение
                memory_parts = memory.split()
                if len(memory_parts) > 1 and memory_parts[0] == memory_parts[1]:
                    memory = memory_parts[0]

            # Исправляем дублирование storage
            if storage and ' ' in storage:
                # Если storage содержит пробелы, берем только первое значение
                storage_parts = storage.split()
                if len(storage_parts) > 1 and storage_parts[0] == storage_parts[1]:
                    storage = storage_parts[0]
            
            # Если размер не указан, извлекаем из generation
            if not size:
                size = self._extract_size(generation)

            # Создаем или обновляем запись
            macbook, created = MacBook.objects.update_or_create(
                generation=generation,
                variant=variant,
                size=size,
                memory=memory,
                storage=storage,
                color=color,
                country=country,
                defaults={
                    'product_code': product_code,
                    'price': Decimal(price),
                    'source': source
                }
            )

            if created:
                logger.info(f"Создан новый MacBook: {macbook.full_name} - {price}₽")
            else:
                logger.info(f"Обновлен MacBook: {macbook.full_name} - {price}₽")

            return macbook

        except Exception as e:
            logger.error(f"Ошибка сохранения MacBook: {e}")
            return None

    def _parse_configuration(self, configuration: str) -> tuple:
        """Парсит конфигурацию для извлечения памяти, хранилища и цвета"""
        import re
        
        # Извлекаем память (8GB, 16GB, 24GB, etc.)
        memory_match = re.search(r'(\d+GB)', configuration)
        memory = memory_match.group(1) if memory_match else '8GB'
        
        # Извлекаем хранилище (256GB, 512GB, 1TB, etc.)
        storage_match = re.search(r'(\d+(?:GB|TB))', configuration)
        storage = storage_match.group(1) if storage_match else '256GB'
        
        # Извлекаем цвет (последнее слово в конфигурации)
        color_parts = configuration.split()
        color = color_parts[-1] if color_parts else 'Space Gray'
        
        return memory, storage, color

    def _extract_size(self, generation: str) -> str:
        """Извлекает размер экрана из generation"""
        import re
        
        # Ищем размер в generation (13, 14, 15, 16)
        size_match = re.search(r'(\d+)(?:\s|$)', generation)
        return size_match.group(1) if size_match else None

    @sync_to_async
    def get_macbook_catalog(self) -> List[Dict[str, Any]]:
        """Получает каталог MacBook как список"""
        try:
            # Получаем все MacBook
            macbooks = MacBook.objects.all().order_by('generation', 'variant', 'size', 'memory', 'storage', 'color', 'country')
            
            macbook_list = []
            for macbook in macbooks:
                # Формируем название
                name_parts = [f"MacBook {macbook.generation}"]
                if macbook.variant:
                    name_parts.append(macbook.variant)
                if macbook.size:
                    name_parts.append(f"{macbook.size}")
                
                # Формируем конфигурацию
                config_parts = []
                if macbook.memory:
                    config_parts.append(macbook.memory)
                if macbook.storage:
                    config_parts.append(macbook.storage)
                if macbook.color:
                    config_parts.append(macbook.color)
                configuration = " ".join(config_parts)
                
                macbook_list.append({
                    'id': macbook.id,
                    'name': " ".join(name_parts),
                    'configuration': configuration,
                    'price': int(macbook.price),
                    'display_price': macbook.display_price,
                    'country': macbook.country,
                    'product_code': macbook.product_code or '',
                    'generation': macbook.generation or '',
                    'variant': macbook.variant or 'Air',
                    'size': macbook.size or '',
                    'memory': macbook.memory or '',
                    'storage': macbook.storage or '',
                    'color': macbook.color or ''
                })
            
            return macbook_list
        except Exception as e:
            logger.error(f"Ошибка получения каталога MacBook: {e}")
            return []

# Создаем глобальный экземпляр
macbook_service_simple = MacBookServiceSimple()
