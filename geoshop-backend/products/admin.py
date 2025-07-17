from django.contrib import admin
from .models import Product, StoreProduct, ClientCart, CartItem

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'package_type', 'quantity', 'weight_unit', 'admin']
    list_filter = ['package_type', 'weight_unit', 'admin']
    search_fields = ['name']

class StoreProductAdmin(admin.ModelAdmin):
    list_display = ['product', 'store', 'price', 'bulk_price', 'bulk_min_quantity', 'loyalty_price', 'is_active']
    list_filter = ['store', 'is_active']
    search_fields = ['product__name', 'store__username']

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0

class ClientCartAdmin(admin.ModelAdmin):
    list_display = ['client', 'created_at', 'updated_at', 'is_completed']
    list_filter = ['is_completed', 'client']
    inlines = [CartItemInline]
    search_fields = ['client__username']

admin.site.register(Product, ProductAdmin)
admin.site.register(StoreProduct, StoreProductAdmin)
admin.site.register(ClientCart, ClientCartAdmin)