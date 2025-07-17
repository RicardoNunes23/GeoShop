from django.db import models
from users.models import CustomUser

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

class StoreProduct(models.Model):
    store = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='store_products', limit_choices_to={'user_type': 'store'})
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='store_products')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    bulk_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    bulk_min_quantity = models.PositiveIntegerField(blank=True, null=True)
    loyalty_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.store.username} - {self.product.name}"

class ClientCart(models.Model):
    client = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='carts', limit_choices_to={'user_type': 'client'})
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Carrinho de {self.client.username} - {self.created_at}"

class CartItem(models.Model):
    cart = models.ForeignKey(ClientCart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Mudei de StoreProduct para Product
    quantity = models.PositiveIntegerField()
    selected_store_product = models.ForeignKey(
        StoreProduct, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Produto da loja selecionada"
    )
    selected_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.quantity}x {self.product.name} no carrinho {self.cart.id}"

    def save(self, *args, **kwargs):
        # Encontra a melhor oferta para este produto
        store_products = StoreProduct.objects.filter(
            product=self.product,
            is_active=True
        ).select_related('store')
        
        best_offer = None
        best_price = None
        
        for sp in store_products:
            # Calcula o preço considerando quantidade e fidelidade
            if self.quantity >= (sp.bulk_min_quantity or 0):
                price = sp.bulk_price or sp.price
            else:
                price = sp.price
            
            # Se for a primeira oferta ou melhor que a atual
            if best_price is None or price < best_price:
                best_price = price
                best_offer = sp
        
        self.selected_store_product = best_offer
        self.selected_price = best_price
        
        super().save(*args, **kwargs)

    def get_available_stores(self):
        """Retorna todas as lojas que oferecem este produto com seus preços"""
        store_products = StoreProduct.objects.filter(
            product=self.product,
            is_active=True
        ).select_related('store')
        
        stores_data = []
        for sp in store_products:
            stores_data.append({
                'store_id': sp.store.id,
                'store_name': sp.store.username,
                'price': sp.price,
                'bulk_price': sp.bulk_price,
                'bulk_min_quantity': sp.bulk_min_quantity,
                'loyalty_price': sp.loyalty_price,
                'final_price': sp.bulk_price if self.quantity >= (sp.bulk_min_quantity or 0) else sp.price
            })
        
        return sorted(stores_data, key=lambda x: x['final_price'])