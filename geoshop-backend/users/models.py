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

    def __str__(self):
        return self.username