"""
Простой сервис каталога
"""
import logging
import os
import django
from django.conf import settings
from asgiref.sync import sync_to_async

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'db_app.settings')
django.setup()

from db_app.models import IPhone, Product, Markup, MacBook, iPad, AppleWatch, iMac, AirPods, ApplePencil
from services.macbook_service_simple import macbook_service_simple

logger = logging.getLogger(__name__)

class CatalogService:
    """Простой сервис для каталога"""
    
    @sync_to_async
    def get_catalog_data(self):
        """Получает данные каталога"""
        try:
            catalog = {}
            
            # iPhone каталог как список
            iphone_data = self._get_iphone_catalog()
            if iphone_data:
                catalog['Apple'] = {'iPhone': iphone_data}
            
            # MacBook каталог
            macbook_data = self._get_macbook_catalog()
            if macbook_data:
                if 'Apple' not in catalog:
                    catalog['Apple'] = {}
                catalog['Apple']['MacBook'] = macbook_data
            
            # iPad каталог
            ipad_data = self._get_ipad_catalog()
            if ipad_data:
                if 'Apple' not in catalog:
                    catalog['Apple'] = {}
                catalog['Apple']['iPad'] = ipad_data
            
            # Apple Watch каталог
            apple_watch_data = self._get_apple_watch_catalog()
            if apple_watch_data:
                if 'Apple' not in catalog:
                    catalog['Apple'] = {}
                catalog['Apple']['Apple Watch'] = apple_watch_data
            
            # iMac каталог
            imac_data = self._get_imac_catalog()
            if imac_data:
                if 'Apple' not in catalog:
                    catalog['Apple'] = {}
                catalog['Apple']['iMac'] = imac_data
            
            # AirPods каталог
            airpods_data = self._get_airpods_catalog()
            if airpods_data:
                if 'Apple' not in catalog:
                    catalog['Apple'] = {}
                catalog['Apple']['AirPods'] = airpods_data
            
            # Apple Pencil каталог
            apple_pencil_data = self._get_apple_pencil_catalog()
            if apple_pencil_data:
                if 'Apple' not in catalog:
                    catalog['Apple'] = {}
                catalog['Apple']['Apple Pencil'] = apple_pencil_data
            
            # Другие товары
            other_data = self._get_other_products_catalog()
            if other_data:
                for brand, categories in other_data.items():
                    if brand not in catalog:
                        catalog[brand] = {}
                    catalog[brand].update(categories)
            
            return catalog
        except Exception as e:
            logger.error(f"Ошибка получения каталога: {e}")
            return {}
    
    def _get_iphone_catalog(self):
        """Получает каталог iPhone как список"""
        try:
            # Получаем все iPhone
            iphones = IPhone.objects.all().order_by('generation', 'variant', 'storage', 'color', 'country')
            
            iphone_list = []
            for iphone in iphones:
                # Формируем название
                name_parts = [f"iPhone {iphone.generation}"]
                if iphone.variant and iphone.variant != "обычный":
                    name_parts.append(iphone.variant)
                
                # Формируем конфигурацию
                config_parts = []
                if iphone.storage:
                    config_parts.append(iphone.storage)
                if iphone.color:
                    config_parts.append(iphone.color)
                configuration = " ".join(config_parts)
                
                iphone_list.append({
                    'id': iphone.id,
                    'name': " ".join(name_parts),
                    'configuration': configuration,
                    'price': int(iphone.price),
                    'display_price': iphone.display_price,
                    'country': iphone.country
                })
            
            return iphone_list
        except Exception as e:
            logger.error(f"Ошибка получения каталога iPhone: {e}")
            return []
    
    def _get_macbook_catalog(self):
        """Получает каталог MacBook"""
        try:
            # Получаем все MacBook из собственной модели
            macbooks = MacBook.objects.all().order_by('generation', 'variant', 'size', 'memory', 'storage', 'color', 'country')
            
            macbook_list = []
            
            for macbook in macbooks:
                # Формируем название
                name_parts = ["MacBook"]
                if macbook.variant:
                    name_parts.append(macbook.variant)
                if macbook.size:
                    name_parts.append(f"{macbook.size}")
                if macbook.generation:
                    name_parts.append(macbook.generation)
                
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
            return {}
    
    def _get_ipad_catalog(self):
        """Получает каталог iPad как список"""
        try:
            # Получаем все iPad
            ipads = iPad.objects.all().order_by('generation', 'variant', 'size', 'storage', 'color', 'country')
            
            ipad_list = []
            for ipad in ipads:
                # Формируем название
                name_parts = ["iPad"]
                if ipad.variant:
                    name_parts.append(ipad.variant)
                if ipad.size:
                    name_parts.append(f"{ipad.size}")
                if ipad.generation:
                    name_parts.append(ipad.generation)
                
                # Формируем конфигурацию
                config_parts = []
                if ipad.storage:
                    config_parts.append(ipad.storage)
                if ipad.color:
                    config_parts.append(ipad.color)
                if ipad.connectivity:
                    config_parts.append(ipad.connectivity)
                configuration = " ".join(config_parts)
                
                ipad_list.append({
                    'id': ipad.id,
                    'name': " ".join(name_parts),
                    'configuration': configuration,
                    'price': int(ipad.price),
                    'display_price': ipad.display_price,
                    'country': ipad.country,
                    'product_code': ipad.product_code or '',
                    'generation': ipad.generation or '',
                    'variant': ipad.variant or '',
                    'size': ipad.size or '',
                    'storage': ipad.storage or '',
                    'color': ipad.color or '',
                    'connectivity': ipad.connectivity or ''
                })
            
            return ipad_list
        except Exception as e:
            logger.error(f"Ошибка получения каталога iPad: {e}")
            return {}
    
    def _get_other_products_catalog(self):
        """Получает каталог других товаров (не iPhone и не MacBook)"""
        try:
            catalog = {}
            
            # Группируем по брендам и категориям, исключая iPhone и MacBook
            products = Product.objects.exclude(brand='Apple', category__in=['iPhone', 'MacBook']).order_by('brand', 'category', 'name')
            
            for product in products:
                brand = product.brand
                category = product.category
                
                if brand not in catalog:
                    catalog[brand] = {}
                
                if category not in catalog[brand]:
                    catalog[brand][category] = []
                
                catalog[brand][category].append({
                    'id': product.id,
                    'name': product.name,
                    'configuration': product.configuration or '',
                    'price': int(product.price),
                    'display_price': product.display_price,
                    'country': product.country
                })
            
            return catalog
        except Exception as e:
            logger.error(f"Ошибка получения каталога других товаров: {e}")
            return {}
    
    def _get_apple_watch_catalog(self):
        """Получает каталог Apple Watch как список"""
        try:
            # Получаем все Apple Watch
            apple_watches = AppleWatch.objects.all().order_by('series', 'size', 'case_color', 'band_type')
            
            apple_watch_list = []
            for watch in apple_watches:
                # Формируем название
                name_parts = ["Apple Watch"]
                if watch.series:
                    name_parts.append(watch.series)
                if watch.size:
                    name_parts.append(f"{watch.size}mm")
                
                # Формируем конфигурацию
                config_parts = []
                if watch.case_color:
                    config_parts.append(watch.case_color)
                if watch.band_type and watch.band_color:
                    config_parts.append(f"{watch.band_type} {watch.band_color}")
                elif watch.band_type:
                    config_parts.append(watch.band_type)
                elif watch.band_color:
                    config_parts.append(watch.band_color)
                if watch.band_size:
                    config_parts.append(f"({watch.band_size})")
                if watch.connectivity:
                    config_parts.append(watch.connectivity)
                
                configuration = " ".join(config_parts)
                
                apple_watch_list.append({
                    'id': watch.id,
                    'name': " ".join(name_parts),
                    'configuration': configuration,
                    'price': int(watch.price),
                    'display_price': watch.display_price,
                    'country': watch.country,
                    'product_code': watch.product_code or '',
                    'series': watch.series or '',
                    'size': watch.size or '',
                    'case_color': watch.case_color or '',
                    'band_type': watch.band_type or '',
                    'band_color': watch.band_color or '',
                    'band_size': watch.band_size or '',
                    'connectivity': watch.connectivity or ''
                })
            
            return apple_watch_list
        except Exception as e:
            logger.error(f"Ошибка получения каталога Apple Watch: {e}")
            return {}
    
    def _get_imac_catalog(self):
        """Получает каталог iMac"""
        try:
            imacs = iMac.objects.all().order_by('model', 'chip', 'size')
            
            imac_list = []
            for imac in imacs:
                # Формируем название
                name_parts = [imac.model]
                if imac.chip:
                    name_parts.append(imac.chip)
                if imac.size and imac.size != 'Mini':
                    name_parts.append(f"{imac.size}\"")
                
                # Формируем конфигурацию
                config_parts = []
                if imac.memory:
                    config_parts.append(imac.memory)
                if imac.storage:
                    config_parts.append(imac.storage)
                if imac.color:
                    config_parts.append(imac.color)
                
                configuration = " ".join(config_parts)
                
                imac_list.append({
                    'id': imac.id,
                    'name': " ".join(name_parts),
                    'configuration': configuration,
                    'price': int(imac.price),
                    'display_price': imac.display_price,
                    'country': imac.country,
                    'product_code': imac.product_code or '',
                    'model': imac.model or '',
                    'chip': imac.chip or '',
                    'size': imac.size or '',
                    'memory': imac.memory or '',
                    'storage': imac.storage or '',
                    'color': imac.color or ''
                })
            
            return imac_list
        except Exception as e:
            logger.error(f"Ошибка получения каталога iMac: {e}")
            return {}
    
    def _get_airpods_catalog(self):
        """Получает каталог AirPods"""
        try:
            airpods = AirPods.objects.all().order_by('model', 'generation', 'features')
            
            airpods_list = []
            for ap in airpods:
                # Формируем название
                name_parts = [ap.model]
                if ap.generation and ap.generation != ap.model:
                    name_parts.append(ap.generation)
                
                # Формируем конфигурацию
                config_parts = []
                if ap.features:
                    config_parts.append(ap.features)
                if ap.color and ap.color != 'White':
                    config_parts.append(ap.color)
                if ap.year:
                    config_parts.append(f"({ap.year})")
                
                configuration = " ".join(config_parts)
                
                airpods_list.append({
                    'id': ap.id,
                    'name': " ".join(name_parts),
                    'configuration': configuration,
                    'price': int(ap.price),
                    'display_price': ap.display_price,
                    'country': ap.country,
                    'product_code': ap.product_code or '',
                    'model': ap.model or '',
                    'generation': ap.generation or '',
                    'features': ap.features or '',
                    'color': ap.color or '',
                    'year': ap.year or ''
                })
            
            return airpods_list
        except Exception as e:
            logger.error(f"Ошибка получения каталога AirPods: {e}")
            return {}
    
    def _get_apple_pencil_catalog(self):
        """Получает каталог Apple Pencil"""
        try:
            pencils = ApplePencil.objects.all().order_by('generation', 'connector')
            
            pencil_list = []
            for pencil in pencils:
                # Формируем название
                name_parts = [pencil.model]
                if pencil.generation:
                    name_parts.append(pencil.generation)
                
                # Формируем конфигурацию
                config_parts = []
                if pencil.connector and pencil.connector != 'Lightning':
                    config_parts.append(f"({pencil.connector})")
                
                configuration = " ".join(config_parts)
                
                pencil_list.append({
                    'id': pencil.id,
                    'name': " ".join(name_parts),
                    'configuration': configuration,
                    'price': int(pencil.price),
                    'display_price': pencil.display_price,
                    'country': pencil.country,
                    'product_code': pencil.product_code or '',
                    'model': pencil.model or '',
                    'generation': pencil.generation or '',
                    'connector': pencil.connector or ''
                })
            
            return pencil_list
        except Exception as e:
            logger.error(f"Ошибка получения каталога Apple Pencil: {e}")
            return {}
    
    @sync_to_async
    def get_current_markup(self):
        """Получает текущую наценку"""
        try:
            return Markup.get_current_markup()
        except Exception as e:
            logger.error(f"Ошибка получения наценки: {e}")
            return 0

# Создаем глобальный экземпляр
catalog_service = CatalogService()
