"""
Django модели для работы с базой данных товаров и цен
"""
from django.db import models
from django.utils import timezone

class IPhone(models.Model):
    """Модель для iPhone"""
    
    # Основные поля
    generation = models.CharField(max_length=10)  # 13, 14, 15, 16, 16E
    variant = models.CharField(max_length=20, blank=True, null=True)  # Pro, Max, Pro Max, Plus, SE
    storage = models.CharField(max_length=10)  # 128GB, 256GB, 512GB, 1TB
    color = models.CharField(max_length=30)  # Black, White, Blue, Natural, Desert, etc.
    country = models.CharField(max_length=10)  # 🇺🇸, 🇯🇵, 🇮🇳, etc.
    country_code = models.CharField(max_length=10, blank=True, null=True)  # 2SIM, etc.
    
    # Цена
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Метаданные
    source = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "iPhone"
        verbose_name_plural = "iPhone"
        # Уникальность по основным полям
        unique_together = ['generation', 'variant', 'storage', 'color', 'country', 'country_code']
        ordering = ['generation', 'variant', 'storage', 'color']
    
    def __str__(self):
        return self.full_name
    
    @property
    def full_name(self):
        """Полное название iPhone"""
        parts = ["iPhone", self.generation]
        
        if self.variant:
            parts.append(self.variant)
            
        parts.extend([self.storage, self.color])
        
        if self.country_code:
            parts.append(f"{self.country}{self.country_code}")
        else:
            parts.append(self.country)
            
        return " ".join(parts)
    
    @property
    def display_price(self):
        """Цена с наценкой для отображения"""
        try:
            markup = Markup.get_current_markup()
            return int(self.price + markup)
        except:
            return int(self.price)
    
    @property
    def generation_display(self):
        """Красивое отображение поколения"""
        return f"iPhone {self.generation}"
    
    @property
    def variant_display(self):
        """Красивое отображение варианта"""
        if not self.variant:
            return "обычный"
        return self.variant

class MacBook(models.Model):
    """Модель для MacBook"""
    
    # Основные поля
    generation = models.CharField(max_length=20)  # M1 13, M2 13, M3 13, M4 13, M4 15, M1 Max 16, etc.
    variant = models.CharField(max_length=20, blank=True, null=True)  # Air, Pro
    size = models.CharField(max_length=10, blank=True, null=True)  # 13, 14, 15, 16
    memory = models.CharField(max_length=20)  # 8GB, 16GB, 24GB, 32GB, 48GB, 128GB
    storage = models.CharField(max_length=20)  # 256GB, 512GB, 1TB, 2TB, 4TB
    color = models.CharField(max_length=30)  # Space Gray, Silver, Midnight, Starlight, Sky Blue, etc.
    country = models.CharField(max_length=10)  # 🇺🇸, 🇯🇵, 🇮🇳, etc.
    
    # Цена и код продукта
    price = models.DecimalField(max_digits=10, decimal_places=2)
    product_code = models.CharField(max_length=50, blank=True, null=True)  # MGN63, MC7X4, etc.
    
    # Метаданные
    source = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "MacBook"
        verbose_name_plural = "MacBook"
        # Уникальность по основным полям
        unique_together = ['generation', 'variant', 'size', 'memory', 'storage', 'color', 'country']
        ordering = ['generation', 'variant', 'size', 'memory', 'storage', 'color']
    
    def __str__(self):
        return self.full_name
    
    @property
    def full_name(self):
        """Полное название MacBook"""
        parts = ["MacBook"]
        
        if self.variant:
            parts.append(self.variant)
            
        if self.size:
            parts.append(self.size)
            
        parts.extend([self.memory, self.storage, self.color])
        parts.append(self.country)
            
        return " ".join(parts)
    
    @property
    def display_price(self):
        """Цена с наценкой для отображения"""
        try:
            markup = Markup.get_current_markup()
            return int(self.price + markup)
        except:
            return int(self.price)
    
    @property
    def generation_display(self):
        """Красивое отображение поколения"""
        return f"MacBook {self.generation}"
    
    @property
    def variant_display(self):
        """Красивое отображение варианта"""
        if not self.variant:
            return "обычный"
        return self.variant

class iPad(models.Model):
    """Модель для iPad"""
    
    # Основные поля
    generation = models.CharField(max_length=20)  # 9, 10, 11, Mini 6, Mini 7, Air 4, Air 11, Air 13, Pro 11, Pro 13
    variant = models.CharField(max_length=20, blank=True, null=True)  # Mini, Air, Pro
    size = models.CharField(max_length=10, blank=True, null=True)  # 9, 10, 11, 13
    storage = models.CharField(max_length=20)  # 64GB, 128GB, 256GB, 512GB, 1TB, 2TB
    color = models.CharField(max_length=30)  # Space Gray, Silver, Pink, Blue, Purple, Yellow, Starlight, etc.
    connectivity = models.CharField(max_length=20, blank=True, null=True)  # Wi-Fi, LTE
    country = models.CharField(max_length=10)  # 🇺🇸, 🇯🇵, 🇮🇳, etc.
    
    # Цена и код продукта
    price = models.DecimalField(max_digits=10, decimal_places=2)
    product_code = models.CharField(max_length=50, blank=True, null=True)  # MD4J4, MXND3, etc.
    
    # Метаданные
    source = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "iPad"
        verbose_name_plural = "iPad"
        # Уникальность по основным полям
        unique_together = ['generation', 'variant', 'size', 'storage', 'color', 'connectivity', 'country']
        ordering = ['generation', 'variant', 'size', 'storage', 'color']
    
    def __str__(self):
        return self.full_name
    
    @property
    def full_name(self):
        """Полное название iPad"""
        parts = ["iPad"]
        
        if self.variant:
            parts.append(self.variant)
        
        if self.size:
            parts.append(f"{self.size}")
            
        if self.generation:
            parts.append(self.generation)
            
        parts.extend([self.storage, self.color])
        
        if self.connectivity:
            parts.append(self.connectivity)
        
        if self.country:
            parts.append(self.country)
            
        return " ".join(parts)
    
    @property
    def display_price(self):
        """Цена с наценкой для отображения"""
        try:
            markup = Markup.get_current_markup()
            return int(self.price + markup)
        except:
            return int(self.price)
    
    @property
    def generation_display(self):
        """Красивое отображение поколения"""
        return f"iPad {self.generation}"
    
    @property
    def variant_display(self):
        """Красивое отображение варианта"""
        if not self.variant:
            return "обычный"
        return self.variant

class AppleWatch(models.Model):
    """Модель для Apple Watch"""
    
    # Основные поля
    series = models.CharField(max_length=20)  # SE, S10, Ultra 2, S9, S8, etc.
    size = models.CharField(max_length=10)  # 40, 42, 44, 46, 49
    case_material = models.CharField(max_length=30, blank=True, null=True)  # Aluminum, Titanium, Stainless Steel
    case_color = models.CharField(max_length=30)  # Midnight, Silver, Starlight, Rose Gold, Jet Black, etc.
    band_type = models.CharField(max_length=50, blank=True, null=True)  # Sport Band, Sport Loop, Milanese Loop, Ocean Band, Alpine Loop
    band_color = models.CharField(max_length=50, blank=True, null=True)  # Midnight, Silver, Lake Green, Blue, Black, etc.
    band_size = models.CharField(max_length=10, blank=True, null=True)  # S/M, M/L, S, M, L
    connectivity = models.CharField(max_length=20, blank=True, null=True)  # GPS, Cellular, GPS+Cellular
    country = models.CharField(max_length=10)  # 🇺🇸, 🇯🇵, 🇮🇳, etc.
    
    # Цена и код продукта
    price = models.DecimalField(max_digits=10, decimal_places=2)
    product_code = models.CharField(max_length=50, blank=True, null=True)  # MXEC3, MWWH3, etc.
    
    # Метаданные
    source = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Apple Watch"
        verbose_name_plural = "Apple Watch"
        # Уникальность по основным полям
        unique_together = ['series', 'size', 'case_color', 'band_type', 'band_color', 'band_size', 'connectivity', 'country']
        ordering = ['series', 'size', 'case_color', 'band_type']
    
    def __str__(self):
        return self.full_name
    
    @property
    def full_name(self):
        """Полное название Apple Watch"""
        parts = ["Apple Watch"]
        
        if self.series:
            parts.append(self.series)
        
        if self.size:
            parts.append(f"{self.size}mm")
            
        if self.case_color:
            parts.append(self.case_color)
        
        if self.band_type and self.band_color:
            parts.append(f"{self.band_type} {self.band_color}")
        elif self.band_type:
            parts.append(self.band_type)
        elif self.band_color:
            parts.append(self.band_color)
            
        if self.band_size:
            parts.append(f"({self.band_size})")
        
        if self.country:
            parts.append(self.country)
            
        return " ".join(parts)
    
    @property
    def display_price(self):
        """Цена с наценкой для отображения"""
        try:
            markup = Markup.get_current_markup()
            return int(self.price + markup)
        except:
            return int(self.price)
    
    @property
    def series_display(self):
        """Красивое отображение серии"""
        return f"Apple Watch {self.series}"
    
    @property
    def size_display(self):
        """Красивое отображение размера"""
        return f"{self.size}mm"

class iMac(models.Model):
    """Модель для iMac и Mac Mini"""
    
    # Основные поля
    model = models.CharField(max_length=20)  # iMac, Mac Mini
    chip = models.CharField(max_length=20)  # M1, M2, M3, M4
    size = models.CharField(max_length=20, blank=True, null=True)  # 24, Mini
    memory = models.CharField(max_length=20)  # 8GB, 16GB, 24GB, 32GB
    storage = models.CharField(max_length=20)  # 256GB, 512GB, 1TB, 2TB
    color = models.CharField(max_length=30)  # Blue, Silver, Green, Pink, Yellow, Orange, Purple
    country = models.CharField(max_length=10)  # 🇺🇸, 🇯🇵, 🇮🇳, etc.
    
    # Цена и код продукта
    price = models.DecimalField(max_digits=10, decimal_places=2)
    product_code = models.CharField(max_length=50, blank=True, null=True)  # MWUF3, MNH73, etc.
    
    # Метаданные
    source = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "iMac"
        verbose_name_plural = "iMac"
        # Уникальность по основным полям
        unique_together = ['model', 'chip', 'size', 'memory', 'storage', 'color', 'country']
        ordering = ['model', 'chip', 'size', 'memory', 'storage', 'color']
    
    def __str__(self):
        return self.full_name
    
    @property
    def full_name(self):
        """Полное название iMac"""
        parts = [self.model]
        
        if self.chip:
            parts.append(self.chip)
            
        if self.size and self.size != 'Mini':
            parts.append(f"{self.size}\"")
            
        parts.extend([self.memory, self.storage, self.color])
        parts.append(self.country)
            
        return " ".join(parts)
    
    @property
    def display_price(self):
        """Цена с наценкой для отображения"""
        try:
            markup = Markup.get_current_markup()
            return int(self.price + markup)
        except:
            return int(self.price)
    
    @property
    def model_display(self):
        """Красивое отображение модели"""
        return f"{self.model} {self.chip}"

class AirPods(models.Model):
    """Модель для AirPods"""
    
    # Основные поля
    model = models.CharField(max_length=30)  # AirPods, AirPods Pro, AirPods Max
    generation = models.CharField(max_length=20)  # 2, 3, 4, Pro, Pro 2, Max
    features = models.CharField(max_length=30, blank=True, null=True)  # ANC, Lightning, USB-C, NEW
    color = models.CharField(max_length=30)  # White, Purple, Orange, Blue, Pink, etc.
    year = models.CharField(max_length=10, blank=True, null=True)  # 2024, 2023, etc.
    country = models.CharField(max_length=10)  # 🇺🇸, 🇯🇵, 🇮🇳, etc.
    
    # Цена и код продукта
    price = models.DecimalField(max_digits=10, decimal_places=2)
    product_code = models.CharField(max_length=50, blank=True, null=True)  # MPNY3, MTJV3, etc.
    
    # Метаданные
    source = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "AirPods"
        verbose_name_plural = "AirPods"
        # Уникальность по основным полям
        unique_together = ['model', 'generation', 'features', 'color', 'year', 'country']
        ordering = ['model', 'generation', 'features', 'color']
    
    def __str__(self):
        return self.full_name
    
    @property
    def full_name(self):
        """Полное название AirPods"""
        parts = [self.model]
        
        if self.generation and self.generation != self.model:
            parts.append(self.generation)
            
        if self.features:
            parts.append(self.features)
            
        if self.color and self.color != 'White':
            parts.append(self.color)
            
        if self.year:
            parts.append(f"({self.year})")
        
        if self.country:
            parts.append(self.country)
            
        return " ".join(parts)
    
    @property
    def display_price(self):
        """Цена с наценкой для отображения"""
        try:
            markup = Markup.get_current_markup()
            return int(self.price + markup)
        except:
            return int(self.price)
    
    @property
    def model_display(self):
        """Красивое отображение модели"""
        if self.generation and self.generation != self.model:
            return f"{self.model} {self.generation}"
        return self.model

class ApplePencil(models.Model):
    """Модель для Apple Pencil"""
    
    # Основные поля
    model = models.CharField(max_length=30, default='Apple Pencil')  # Apple Pencil
    generation = models.CharField(max_length=20)  # 1, 2, Pro, USB-C
    connector = models.CharField(max_length=20)  # Lightning, USB-C
    country = models.CharField(max_length=10)  # 🇺🇸, 🇯🇵, 🇮🇳, etc.
    
    # Цена и код продукта
    price = models.DecimalField(max_digits=10, decimal_places=2)
    product_code = models.CharField(max_length=50, blank=True, null=True)
    
    # Метаданные
    source = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Apple Pencil"
        verbose_name_plural = "Apple Pencil"
        # Уникальность по основным полям
        unique_together = ['model', 'generation', 'connector', 'country']
        ordering = ['generation', 'connector']
    
    def __str__(self):
        return self.full_name
    
    @property
    def full_name(self):
        """Полное название Apple Pencil"""
        parts = [self.model]
        
        if self.generation:
            parts.append(self.generation)
            
        if self.connector and self.connector != 'Lightning':
            parts.append(f"({self.connector})")
        
        if self.country:
            parts.append(self.country)
            
        return " ".join(parts)
    
    @property
    def display_price(self):
        """Цена с наценкой для отображения"""
        try:
            markup = Markup.get_current_markup()
            return int(self.price + markup)
        except:
            return int(self.price)
    
    @property
    def model_display(self):
        """Красивое отображение модели"""
        if self.generation:
            return f"{self.model} {self.generation}"
        return self.model

class Product(models.Model):
    """Универсальная модель для всех остальных товаров"""
    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    configuration = models.CharField(max_length=200, blank=True, null=True)
    country = models.CharField(max_length=10)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    source = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        unique_together = ['name', 'brand', 'category', 'configuration', 'country']
        ordering = ['brand', 'category', 'name']
    
    def __str__(self):
        return f"{self.brand} {self.name}"
    
    @property
    def display_price(self):
        """Цена с наценкой для отображения"""
        try:
            markup = Markup.get_current_markup()
            return int(self.price + markup)
        except:
            return int(self.price)

class Markup(models.Model):
    """Наценка для отображения цен"""
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Размер наценки в рублях")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'markup'
        verbose_name = "Наценка"
        verbose_name_plural = "Наценки"
        ordering = ['-updated_at']

    def __str__(self):
        return f"Наценка: {self.amount}₽"

    @classmethod
    def get_current_markup(cls):
        """Получает текущую наценку"""
        markup = cls.objects.first()
        return markup.amount if markup else 0

    @classmethod
    def set_markup(cls, amount):
        """Устанавливает новую наценку"""
        cls.objects.all().delete()  # Удаляем старые записи
        cls.objects.create(amount=amount)