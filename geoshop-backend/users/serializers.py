from rest_framework import serializers
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'user_type', 'cnpj', 'address', 
                 'responsible', 'phone', 'latitude', 'longitude', 'use_bulk_pricing', 
                 'has_loyalty_card']
        read_only_fields = ['id', 'user_type']

class ClientRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            user_type='client'
        )
        return user

class StoreRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'cnpj', 'address', 
                'responsible', 'phone', 'latitude', 'longitude', 'use_bulk_pricing', 
                'has_loyalty_card']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            user_type='store',
            cnpj=validated_data.get('cnpj'),
            address=validated_data.get('address'),
            responsible=validated_data.get('responsible'),
            phone=validated_data.get('phone'),
            latitude=validated_data.get('latitude'),
            longitude=validated_data.get('longitude'),
            use_bulk_pricing=validated_data.get('use_bulk_pricing', False),
            has_loyalty_card=validated_data.get('has_loyalty_card', False)
        )
        return user

class StoreUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'cnpj', 'address', 'responsible', 
                'phone', 'latitude', 'longitude', 'use_bulk_pricing', 'has_loyalty_card']
        
    def validate(self, data):
        # Validação adicional para garantir que os campos só sejam usados por lojas
        if self.instance and self.instance.user_type != 'store':
            if 'use_bulk_pricing' in data or 'has_loyalty_card' in data or 'phone' in data:
                raise serializers.ValidationError(
                    "Essas configurações são apenas para lojas"
                )
        return data