from django.contrib import admin
from .models import Plan, StoreSubscription

class PlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'product_limit', 'ativo', 'created_at']
    list_editable = ['ativo']  # Permite ativar/desativar diretamente na lista
    list_filter = ['ativo']  # Adiciona filtro por status
    search_fields = ['name']
    actions = ['ativar_planos', 'desativar_planos']  # Ações em massa

    def ativar_planos(self, request, queryset):
        queryset.update(ativo=True)
    ativar_planos.short_description = "Ativar planos selecionados"

    def desativar_planos(self, request, queryset):
        queryset.update(ativo=False)
    desativar_planos.short_description = "Desativar planos selecionados"

class StoreSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['store', 'plan', 'is_active', 'payment_status', 'created_at']
    list_filter = ['plan', 'is_active', 'payment_status']
    search_fields = ['store__username']

admin.site.register(Plan, PlanAdmin)
admin.site.register(StoreSubscription, StoreSubscriptionAdmin)