# serializers.py
from rest_framework import serializers
from .models import Product, StoreProduct
from users.models import CustomUser
import logging

# Configurar logger
logger = logging.getLogger(__name__)

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
    store_username = serializers.CharField(source='store.username', read_only=True)
    store_latitude = serializers.FloatField(source='store.latitude', read_only=True, allow_null=True)
    store_longitude = serializers.FloatField(source='store.longitude', read_only=True, allow_null=True)

    class Meta:
        model = StoreProduct
        fields = ['id', 'store', 'store_username', 'store_latitude', 'store_longitude', 'product', 'product_id', 'price', 'bulk_price', 'bulk_min_quantity', 'loyalty_price', 'is_active']
        read_only_fields = ['store', 'product', 'store_username', 'store_latitude', 'store_longitude']

    def validate_product_id(self, value):
        logger.debug(f"Validando product_id: {value.id}")
        if not Product.objects.filter(id=value.id).exists():
            logger.error(f"Produto com ID {value.id} não existe")
            raise serializers.ValidationError("Produto com este ID não existe.")
        request = self.context.get('request')
        if request and StoreProduct.objects.filter(product=value, store=request.user).exists():
            instance = self.instance
            if not instance or (instance and instance.product != value):
                logger.warning(f"Produto {value.id} já cadastrado para a loja {request.user.username}")
                raise serializers.ValidationError("Este produto já está cadastrado na loja.")
        return value

    def validate(self, data):
        logger.debug(f"Validando dados: {data}")
        if data.get('price') is None or data.get('price') <= 0:
            logger.error("Preço inválido: deve ser maior que zero")
            raise serializers.ValidationError("O preço deve ser maior que zero.")
        if data.get('bulk_price') is not None and data.get('bulk_price') < 0:
            logger.error("Preço por quantidade inválido: não pode ser negativo")
            raise serializers.ValidationError("O preço por quantidade não pode ser negativo.")
        if data.get('bulk_min_quantity') is not None and data.get('bulk_min_quantity') < 0:
            logger.error("Quantidade mínima inválida: não pode ser negativa")
            raise serializers.ValidationError("A quantidade mínima não pode ser negativa.")
        if data.get('loyalty_price') is not None and data.get('loyalty_price') < 0:
            logger.error("Preço por fidelidade inválido: não pode ser negativo")
            raise serializers.ValidationError("O preço por fidelidade não pode ser negativo.")
        return data

    def create(self, validated_data):
        logger.debug(f"Criando StoreProduct com dados: {validated_data}")
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            logger.error("Contexto de request ou usuário autenticado não disponível")
            raise serializers.ValidationError("Usuário não autenticado ou contexto inválido")
        try:
            store_product = StoreProduct.objects.create(**validated_data)
            logger.info(f"StoreProduct criado com sucesso: ID {store_product.id}")
            return store_product
        except Exception as e:
            logger.error(f"Erro ao criar StoreProduct: {str(e)}")
            raise serializers.ValidationError(f"Erro ao criar produto: {str(e)}")

class ShoppingListItemSerializer(serializers.Serializer):
    store_product = StoreProductSerializer(read_only=True)
    quantity = serializers.IntegerField(min_value=1)
    item_total = serializers.FloatField()

class ShoppingListResultSerializer(serializers.Serializer):
    store_id = serializers.IntegerField()
    store_username = serializers.CharField()
    total_price = serializers.FloatField()
    items = ShoppingListItemSerializer(many=True)
    store_latitude = serializers.FloatField(allow_null=True)
    store_longitude = serializers.FloatField(allow_null=True)