"""
Упрощенный сервис для работы с базой данных
"""
import logging
from typing import List, Dict, Any, Optional, Tuple
from decimal import Decimal
import os
import django
from django.conf import settings
from asgiref.sync import sync_to_async

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'db_app.settings')
django.setup()

from db_app.models import Product, Markup, MacBook

logger = logging.getLogger(__name__)

class DatabaseService:
    """Упрощенный сервис для работы с универсальными товарами"""

    async def process_parsed_prices(self, parsed_prices: List[Dict[str, Any]], source: str = "") -> int:
        """Обрабатывает распарсенные прайсы и сохраняет в БД"""
        from services.iphone_service_simple import iphone_service_simple
        from services.macbook_service_simple import macbook_service_simple
        
        saved_count = 0

        for price_data in parsed_prices:
            try:
                device = price_data.get('device', '').lower()
                firm = price_data.get('firm', '').lower()
                
                # Добавляем source к price_data
                price_data['source'] = source
                
                if firm == 'apple' and device == 'iphone':
                    # Сохраняем iPhone в собственную модель
                    # Создаем строку в формате, который понимает iPhone парсер
                    generation = price_data.get('generation', '')
                    variant = price_data.get('variant', '')
                    configuration = price_data.get('configuration', '')
                    country = price_data.get('country', '')
                    price = price_data.get('price', 0)
                    
                    # Формируем строку в правильном формате
                    if variant:
                        line = f"{generation}{variant} {configuration} {country} {price}"
                    else:
                        line = f"{generation} {configuration} {country} {price}"
                    
                    result = await iphone_service_simple.parse_and_save_prices(line, source)
                    if result and result.get('saved', 0) > 0:
                        saved_count += result['saved']
                elif firm == 'apple' and device == 'macbook':
                    # Сохраняем MacBook в собственную модель
                    saved_item = await macbook_service_simple.save_macbook_price(price_data)
                    if saved_item:
                        saved_count += 1
                else:
                    # Сохраняем остальные товары в универсальную модель
                    if await self._save_product(price_data, source):
                        saved_count += 1
            except Exception as e:
                logger.error(f"Ошибка обработки прайса: {e}")
                continue

        logger.info(f"Обработано {saved_count} прайсов из {len(parsed_prices)}")
        return saved_count

    @sync_to_async
    def _save_product(self, product_data: Dict[str, Any], source: str) -> bool:
        """Сохраняет универсальный продукт"""
        try:
            # Формируем название
            name_parts = []
            if product_data.get('device'):
                name_parts.append(product_data['device'])
            if product_data.get('generation'):
                name_parts.append(product_data['generation'])
            if product_data.get('variant'):
                name_parts.append(product_data['variant'])
            
            name = " ".join(name_parts) if name_parts else "Unknown"
            
            # Создаем или обновляем продукт
            product, created = Product.objects.update_or_create(
                name=name,
                brand=product_data.get('firm', 'Unknown'),
                category=product_data.get('device', 'Unknown'),
                configuration=product_data.get('configuration', ''),
                country=product_data.get('country', '🇺🇸'),
                defaults={
                    'price': Decimal(product_data.get('price', 0)),
                    'source': source
                }
            )
            
            if created:
                logger.info(f"Создан новый продукт: {product}")
            else:
                logger.info(f"Обновлен продукт: {product}")
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка сохранения продукта: {e}")
            return False

    @sync_to_async
    def clear_database(self) -> int:
        """Очищает базу данных"""
        try:
            from db_app.models import IPhone, iPad, AppleWatch
            
            # Подсчитываем количество записей в каждой модели
            count_iphone = IPhone.objects.count()
            count_macbook = MacBook.objects.count()
            count_ipad = iPad.objects.count()
            count_apple_watch = AppleWatch.objects.count()
            count_product = Product.objects.count()
            
            # Удаляем все записи
            IPhone.objects.all().delete()
            MacBook.objects.all().delete()
            iPad.objects.all().delete()
            AppleWatch.objects.all().delete()
            Product.objects.all().delete()
            
            total_count = count_iphone + count_macbook + count_ipad + count_apple_watch + count_product
            logger.info(f"Очищена база данных: удалено {total_count} товаров (iPhone: {count_iphone}, MacBook: {count_macbook}, iPad: {count_ipad}, Apple Watch: {count_apple_watch}, Product: {count_product})")
            return total_count
        except Exception as e:
            logger.error(f"Ошибка очистки базы данных: {e}")
            return 0

    @sync_to_async
    def get_current_markup(self) -> float:
        """Получает текущую наценку"""
        try:
            return float(Markup.get_current_markup())
        except Exception as e:
            logger.error(f"Ошибка получения наценки: {e}")
            return 0.0

    @sync_to_async
    def set_markup(self, amount: float) -> bool:
        """Устанавливает новую наценку"""
        try:
            Markup.set_markup(amount)
            logger.info(f"Установлена новая наценка: {amount}₽")
            return True
        except Exception as e:
            logger.error(f"Ошибка установки наценки: {e}")
            return False

db_service = DatabaseService()