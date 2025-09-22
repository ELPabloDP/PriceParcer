from django.contrib import admin
from .models import IPhone, Product, Markup

@admin.register(IPhone)
class IPhoneAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'price', 'display_price', 'source', 'created_at']
    list_filter = ['generation', 'variant', 'storage', 'country']
    search_fields = ['generation', 'variant', 'color']
    ordering = ['-created_at']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'category', 'price', 'display_price', 'country', 'created_at']
    list_filter = ['brand', 'category', 'country']
    search_fields = ['name', 'brand', 'category']
    ordering = ['-created_at']

@admin.register(Markup)
class MarkupAdmin(admin.ModelAdmin):
    list_display = ['amount', 'created_at']
    ordering = ['-created_at']