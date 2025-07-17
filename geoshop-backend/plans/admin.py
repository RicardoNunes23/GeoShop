from django.contrib import admin
from .models import Plan, StoreSubscription

class PlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'product_limit']
    search_fields = ['name']

class StoreSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['store', 'plan', 'is_active', 'payment_status', 'created_at']
    list_filter = ['plan', 'is_active', 'payment_status']
    search_fields = ['store__username']

admin.site.register(Plan, PlanAdmin)
admin.site.register(StoreSubscription, StoreSubscriptionAdmin)