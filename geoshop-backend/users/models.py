from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('client', 'Cliente'),
        ('store', 'Loja'),
    )
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='client')
    cnpj = models.CharField(max_length=18, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    responsible = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone de Contato")
    
    # Campos específicos para lojas
    use_bulk_pricing = models.BooleanField(
        default=False,
        verbose_name="Trabalha com quantidade mínima?",
        help_text="Ative para permitir preços por quantidade nos produtos"
    )
    has_loyalty_card = models.BooleanField(
        default=False,
        verbose_name="Oferece cartão fidelidade?",
        help_text="Ative para permitir preços especiais para clientes fidelizados"
    )

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        # Garante que os campos só sejam válidos para lojas
        if self.user_type != 'store':
            self.use_bulk_pricing = False
            self.has_loyalty_card = False
            self.phone = None
        super().save(*args, **kwargs)