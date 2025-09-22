"""
Специализированные модели для iPhone
"""
from django.db import models
from django.utils import timezone

class IPhoneGeneration(models.Model):
    """Поколения iPhone (13, 14, 15, 16)"""
    number = models.CharField(max_length=10, unique=True)  # 13, 14, 15, 16, 16E
    display_name = models.CharField(max_length=50)  # iPhone 13, iPhone 14, etc.
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Поколение iPhone"
        verbose_name_plural = "Поколения iPhone"
        ordering = ['number']
    
    def __str__(self):
        return self.display_name

class IPhoneVariant(models.Model):
    """Варианты iPhone (обычный, Plus, Pro, Pro Max)"""
    name = models.CharField(max_length=20, unique=True)  # "", "Plus", "Pro", "Pro Max"
    display_name = models.CharField(max_length=50)  # iPhone 15, iPhone 15 Plus, etc.
    sort_order = models.IntegerField(default=0)  # Для сортировки в каталоге
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Вариант iPhone"
        verbose_name_plural = "Варианты iPhone"
        ordering = ['sort_order']
    
    def __str__(self):
        return self.display_name

class IPhoneStorage(models.Model):
    """Объем памяти iPhone"""
    capacity = models.CharField(max_length=10, unique=True)  # 128GB, 256GB, 512GB, 1TB
    size_gb = models.IntegerField()  # Для сортировки
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Объем памяти iPhone"
        verbose_name_plural = "Объемы памяти iPhone"
        ordering = ['size_gb']
    
    def __str__(self):
        return self.capacity

class IPhoneColor(models.Model):
    """Цвета iPhone"""
    name = models.CharField(max_length=30, unique=True)  # Black, White, Blue, etc.
    display_name = models.CharField(max_length=50)  # Для красивого отображения
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Цвет iPhone"
        verbose_name_plural = "Цвета iPhone"
        ordering = ['name']
    
    def __str__(self):
        return self.display_name

class IPhoneCountry(models.Model):
    """Страны для iPhone"""
    flag = models.CharField(max_length=5, unique=True)  # 🇺🇸, 🇯🇵, etc.
    name = models.CharField(max_length=50)  # США, Япония, etc.
    code = models.CharField(max_length=5, blank=True)  # 2SIM, etc.
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Страна iPhone"
        verbose_name_plural = "Страны iPhone"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.flag} {self.name}"

class IPhonePrice(models.Model):
    """Цены на iPhone"""
    generation = models.ForeignKey(IPhoneGeneration, on_delete=models.CASCADE, related_name='prices')
    variant = models.ForeignKey(IPhoneVariant, on_delete=models.CASCADE, related_name='prices')
    storage = models.ForeignKey(IPhoneStorage, on_delete=models.CASCADE, related_name='prices')
    color = models.ForeignKey(IPhoneColor, on_delete=models.CASCADE, related_name='prices')
    country = models.ForeignKey(IPhoneCountry, on_delete=models.CASCADE, related_name='prices')
    
    price = models.DecimalField(max_digits=10, decimal_places=2)
    source = models.CharField(max_length=200, blank=True)  # Источник цены
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Цена iPhone"
        verbose_name_plural = "Цены iPhone"
        unique_together = ['generation', 'variant', 'storage', 'color', 'country']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.full_name} - {self.price:,}₽"
    
    @property
    def full_name(self):
        """Полное название iPhone"""
        parts = ["iPhone", self.generation.number]
        if self.variant.name:  # Если не обычный
            parts.append(self.variant.name)
        parts.extend([self.storage.capacity, self.color.display_name])
        return " ".join(parts)
    
    @property
    def display_price(self):
        """Цена с наценкой для отображения"""
        from .models import Markup
        markup = Markup.get_current_markup()
        return int(self.price + markup)

class IPhoneBestPrice(models.Model):
    """Лучшие цены на iPhone (самые дешевые)"""
    generation = models.ForeignKey(IPhoneGeneration, on_delete=models.CASCADE)
    variant = models.ForeignKey(IPhoneVariant, on_delete=models.CASCADE)
    storage = models.ForeignKey(IPhoneStorage, on_delete=models.CASCADE)
    color = models.ForeignKey(IPhoneColor, on_delete=models.CASCADE)
    
    best_price = models.ForeignKey(IPhonePrice, on_delete=models.CASCADE, related_name='best_for')
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Лучшая цена iPhone"
        verbose_name_plural = "Лучшие цены iPhone"
        unique_together = ['generation', 'variant', 'storage', 'color']
        ordering = ['generation__number', 'variant__sort_order', 'storage__size_gb']
    
    def __str__(self):
        return f"Лучшая цена: {self.best_price.full_name} - {self.best_price.price:,}₽"
