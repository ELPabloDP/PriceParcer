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

from db_app.models import (
    Brand, ProductCategory, ProductModel, ProductVariant, 
    ProductSpecification, ProductColor, Country, Product, 
    PriceRecord, BestPrice
)

logger = logging.getLogger(__name__)

class DatabaseService:
    """Сервис для работы с базой данных товаров и цен"""
    
    def __init__(self):
        self.country_flags = {
            "🇺🇸": "США",
            "🇰🇷": "Южная Корея", 
            "🇪🇺": "Европа",
            "🇭🇰": "Гонконг",
            "🇮🇳": "Индия",
            "🇦🇪": "ОАЭ",
            "🇷🇺": "Россия",
            "🇨🇳": "Китай",
            "🇯🇵": "Япония"
        }
    
    def get_or_create_brand(self, brand_name: str) -> Brand:
        """Получает или создает бренд"""
        brand, created = Brand.objects.get_or_create(
            name=brand_name,
            defaults={'name': brand_name}
        )
        if created:
            logger.info(f"Создан новый бренд: {brand_name}")
        return brand
    
    def get_or_create_category(self, brand: Brand, category_name: str) -> ProductCategory:
        """Получает или создает категорию продукта"""
        category, created = ProductCategory.objects.get_or_create(
            name=category_name,
            brand=brand,
            defaults={'name': category_name, 'brand': brand}
        )
        if created:
            logger.info(f"Создана новая категория: {brand.name} {category_name}")
        return category
    
    def get_or_create_model(self, category: ProductCategory, model_name: str) -> ProductModel:
        """Получает или создает модель продукта"""
        model, created = ProductModel.objects.get_or_create(
            name=model_name,
            category=category,
            defaults={'name': model_name, 'category': category}
        )
        if created:
            logger.info(f"Создана новая модель: {category} {model_name}")
        return model
    
    def get_or_create_variant(self, category: ProductCategory, variant_name: str) -> Optional[ProductVariant]:
        """Получает или создает вариант продукта"""
        if not variant_name:
            return None
            
        variant, created = ProductVariant.objects.get_or_create(
            name=variant_name,
            category=category,
            defaults={'name': variant_name, 'category': category}
        )
        if created:
            logger.info(f"Создан новый вариант: {category} {variant_name}")
        return variant
    
    def get_or_create_specification(self, category: ProductCategory, spec_name: str) -> Optional[ProductSpecification]:
        """Получает или создает спецификацию продукта"""
        if not spec_name:
            return None
            
        spec, created = ProductSpecification.objects.get_or_create(
            name=spec_name,
            category=category,
            defaults={'name': spec_name, 'category': category}
        )
        if created:
            logger.info(f"Создана новая спецификация: {category} {spec_name}")
        return spec
    
    def get_or_create_color(self, category: ProductCategory, color_name: str) -> Optional[ProductColor]:
        """Получает или создает цвет продукта"""
        if not color_name:
            return None
            
        color, created = ProductColor.objects.get_or_create(
            name=color_name,
            category=category,
            defaults={'name': color_name, 'category': color_name}
        )
        if created:
            logger.info(f"Создан новый цвет: {category} {color_name}")
        return color
    
    def get_or_create_country(self, country_flag: str) -> Country:
        """Получает или создает страну"""
        country_name = self.country_flags.get(country_flag, "Неизвестная страна")
        
        country, created = Country.objects.get_or_create(
            flag=country_flag,
            defaults={'name': country_name, 'flag': country_flag}
        )
        if created:
            logger.info(f"Создана новая страна: {country_flag} {country_name}")
        return country
    
    def parse_configuration(self, config: str) -> Tuple[Optional[str], Optional[str]]:
        """Парсит конфигурацию на спецификацию и цвет"""
        if not config:
            return None, None
            
        # Простая логика парсинга - можно улучшить
        parts = config.split()
        spec_parts = []
        color_parts = []
        
        # Цвета обычно в конце
        color_keywords = ['Midnight', 'Blue', 'Starlight', 'Green', 'Pink', 'Red', 'Gold', 'Graphite', 
                         'Purple', 'Silver', 'Gray', 'Black', 'White', 'Rose', 'Cobalt', 'Indigo',
                         'Sterling', 'Jasper', 'Ceramic', 'Prussian', 'Vinca', 'Topaz']
        
        for part in parts:
            if any(color in part for color in color_keywords):
                color_parts.append(part)
            else:
                spec_parts.append(part)
        
        spec = " ".join(spec_parts) if spec_parts else None
        color = " ".join(color_parts) if color_parts else None
        
        return spec, color
    
    def create_or_update_product(self, product_data: Dict[str, Any]) -> Optional[Product]:
        """Создает или обновляет продукт в базе данных"""
        try:
            # Получаем или создаем бренд
            brand = self.get_or_create_brand(product_data.get('firm', ''))
            
            # Получаем или создаем категорию
            category = self.get_or_create_category(brand, product_data.get('device', ''))
            
            # Получаем или создаем модель
            model = self.get_or_create_model(category, product_data.get('generation', ''))
            
            # Получаем или создаем вариант
            variant = self.get_or_create_variant(category, product_data.get('variant', ''))
            
            # Парсим конфигурацию
            spec_name, color_name = self.parse_configuration(product_data.get('configuration', ''))
            
            # Получаем или создаем спецификацию и цвет
            specification = self.get_or_create_specification(category, spec_name) if spec_name else None
            color = self.get_or_create_color(category, color_name) if color_name else None
            
            # Получаем или создаем страну
            country = self.get_or_create_country(product_data.get('country', ''))
            
            # Создаем или получаем продукт
            product, created = Product.objects.get_or_create(
                model=model,
                variant=variant,
                specification=specification,
                color=color,
                country=country,
                defaults={
                    'product_code': product_data.get('product_code', ''),
                    'model': model,
                    'variant': variant,
                    'specification': specification,
                    'color': color,
                    'country': country
                }
            )
            
            if created:
                logger.info(f"Создан новый продукт: {product.full_name}")
            
            return product
            
        except Exception as e:
            logger.error(f"Ошибка создания продукта: {e}")
            return None
    
    def save_price_record(self, product: Product, price: int, source: str = "") -> Optional[PriceRecord]:
        """Сохраняет запись о цене"""
        try:
            # Создаем запись о цене
            price_record = PriceRecord.objects.create(
                product=product,
                price=Decimal(price),
                source=source
            )
            
            # Обновляем лучшую цену
            self.update_best_price(product, price_record)
            
            logger.info(f"Сохранена цена: {product.full_name} - {price}₽")
            return price_record
            
        except Exception as e:
            logger.error(f"Ошибка сохранения цены: {e}")
            return None
    
    def update_best_price(self, product: Product, new_price_record: PriceRecord):
        """Обновляет лучшую цену для продукта"""
        try:
            best_price, created = BestPrice.objects.get_or_create(
                product=product,
                defaults={'price_record': new_price_record}
            )
            
            if not created:
                # Если новая цена лучше (меньше), обновляем
                if new_price_record.final_price < best_price.price_record.final_price:
                    best_price.price_record = new_price_record
                    best_price.save()
                    logger.info(f"Обновлена лучшая цена для {product.full_name}: {new_price_record.final_price}₽")
            else:
                logger.info(f"Установлена лучшая цена для {product.full_name}: {new_price_record.final_price}₽")
                
        except Exception as e:
            logger.error(f"Ошибка обновления лучшей цены: {e}")
    
    def process_parsed_prices(self, parsed_prices: List[Dict[str, Any]], source: str = "") -> int:
        """Обрабатывает распарсенные прайсы и сохраняет в БД"""
        saved_count = 0
        
        for price_data in parsed_prices:
            try:
                # Создаем или получаем продукт
                product = self.create_or_update_product(price_data)
                if not product:
                    continue
                
                # Сохраняем цену
                price = price_data.get('price', 0)
                if price and price > 0:
                    self.save_price_record(product, price, source)
                    saved_count += 1
                    
            except Exception as e:
                logger.error(f"Ошибка обработки прайса: {e}")
                continue
        
        logger.info(f"Обработано {saved_count} прайсов из {len(parsed_prices)}")
        return saved_count
    
    def get_catalog_data(self) -> Dict[str, Any]:
        """Получает данные для каталога"""
        try:
            brands = Brand.objects.all().order_by('name')
            catalog = {}
            
            for brand in brands:
                categories = brand.categories.all().order_by('name')
                brand_data = {}
                
                for category in categories:
                    models = category.models.all().order_by('name')
                    category_data = {}
                    
                    for model in models:
                        # Получаем лучшие цены для этой модели
                        products = model.products.all()
                        model_data = []
                        
                        for product in products:
                            if hasattr(product, 'best_price') and product.best_price:
                                price_record = product.best_price.price_record
                                model_data.append({
                                    'id': product.id,
                                    'name': product.full_name,
                                    'price': int(price_record.final_price),
                                    'country': product.country.flag
                                })
                        
                        if model_data:
                            category_data[model.name] = model_data
                    
                    if category_data:
                        brand_data[category.name] = category_data
                
                if brand_data:
                    catalog[brand.name] = brand_data
            
            return catalog
            
        except Exception as e:
            logger.error(f"Ошибка получения данных каталога: {e}")
            return {}
    
    def clear_database(self) -> int:
        """Очищает базу данных"""
        try:
            from db_app.models import IPhone, MacBook, iPad, AppleWatch
            
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

# Создаем глобальный экземпляр
db_service = DatabaseService()
