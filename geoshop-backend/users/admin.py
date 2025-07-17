# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'user_type', 'is_staff', 'use_bulk_pricing', 'has_loyalty_card']
    
    # Campos para edição
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('user_type', 'cnpj', 'address', 'responsible', 'latitude', 'longitude')}),
        ('Configurações da Loja', {
            'fields': ('use_bulk_pricing', 'has_loyalty_card'),
            'classes': ('collapse',)  # Opcional: mostra em seção recolhível
        }),
    )
    
    # Campos para criação
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {
            'fields': ('user_type', 'cnpj', 'address', 'responsible', 'latitude', 'longitude')
        }),
    )
    
    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj and obj.user_type == 'store':
            # Mostra os campos específicos apenas para lojas
            return fieldsets + (
                ('Configurações da Loja', {
                    'fields': ('use_bulk_pricing', 'has_loyalty_card'),
                    'classes': ('collapse',)
                }),
            )
        return fieldsets

admin.site.register(CustomUser, CustomUserAdmin)