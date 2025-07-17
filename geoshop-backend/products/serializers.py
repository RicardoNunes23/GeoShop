from rest_framework import serializers
from .models import Product, StoreProduct, ClientCart, CartItem
from users.models import CustomUser

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['admin']

class StoreProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), 
        source='product', 
        write_only=True
    )
    
    class Meta:
        model = StoreProduct
        fields = '__all__'
        read_only_fields = ['store']

    def validate(self, data):
        # Validação para garantir que a loja não pode definir preços menores que zero
        if data.get('price', 0) < 0:
            raise serializers.ValidationError("O preço não pode ser negativo.")
        if data.get('bulk_price', 0) < 0:
            raise serializers.ValidationError("O preço por quantidade não pode ser negativo.")
        if data.get('loyalty_price', 0) < 0:
            raise serializers.ValidationError("O preço por fidelidade não pode ser negativo.")
        return data

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), 
        source='product', 
        write_only=True
    )
    available_stores = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = [
            'id', 'cart', 'product', 'product_id', 'quantity',
            'selected_price', 'selected_store_product', 'available_stores',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'selected_price', 'selected_store_product', 'available_stores'
        ]
    
    def get_available_stores(self, obj):
        return obj.get_available_stores()

class ClientCartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    best_store = serializers.SerializerMethodField()

    class Meta:
        model = ClientCart
        fields = '__all__'
        read_only_fields = ['client', 'is_completed']

    def get_total_price(self, obj):
        return sum(item.selected_price * item.quantity for item in obj.items.all())

    def get_best_store(self, obj):
        # Lógica para encontrar a melhor loja baseada nos itens do carrinho
        from collections import defaultdict
        store_totals = defaultdict(float)
        store_items = defaultdict(int)
        
        for item in obj.items.all():
            store = item.store_product.store
            store_totals[store.id] += item.selected_price * item.quantity
            store_items[store.id] += 1
        
        if not store_totals:
            return None
        
        # Encontra a loja com o menor preço total e maior número de itens
        best_store_id = min(store_totals, key=lambda k: (store_totals[k], -store_items[k]))
        best_store = CustomUser.objects.get(id=best_store_id)
        
        return {
            'id': best_store.id,
            'username': best_store.username,
            'total_price': store_totals[best_store_id],
            'items_count': store_items[best_store_id]
        }