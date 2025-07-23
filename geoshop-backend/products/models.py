from django.db import models
from users.models import CustomUser
from django.core.validators import MinValueValidator

class Product(models.Model):
    PACKAGE_TYPES = (
        ('saco', 'Saco'),
        ('pacote', 'Pacote'),
        ('lata', 'Lata'),
        ('caixa', 'Caixa'),
        ('bandeja', 'Bandeja'),
        ('garrafa', 'Garrafa'),
        ('outro', 'Outro'),
    )
    
    WEIGHT_UNITS = (
        ('kg', 'Quilograma'),
        ('g', 'Grama'),
        ('l', 'Litro'),
        ('ml', 'Mililitro'),
        ('un', 'Unidade'),
    )
    
    admin = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='products', limit_choices_to={'user_type': 'admin'})
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    package_type = models.CharField(max_length=10, choices=PACKAGE_TYPES)
    weight_unit = models.CharField(max_length=2, choices=WEIGHT_UNITS)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.quantity} - {self.weight_unit}"

    class Meta:
        ordering = ['name']

class StoreProduct(models.Model):
    store = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='store_products', limit_choices_to={'user_type': 'store'})
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='store_products')
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    bulk_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    bulk_min_quantity = models.PositiveIntegerField(blank=True, null=True)
    loyalty_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.store.username} - {self.product.name}"

    class Meta:
        unique_together = ('store', 'product')
        ordering = ['product__name']