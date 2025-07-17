from rest_framework import serializers
from .models import Plan, StoreSubscription

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ['id', 'name', 'price', 'product_limit', 'description', 'ativo', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class StoreSubscriptionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)
    plan_id = serializers.PrimaryKeyRelatedField(
        queryset=Plan.objects.filter(ativo=True),  # Só permite planos ativos
        source='plan',
        write_only=True
    )

    class Meta:
        model = StoreSubscription
        fields = ['id', 'store', 'plan', 'plan_id', 'is_active', 'payment_status', 'created_at', 'updated_at']
        read_only_fields = ['store', 'is_active', 'payment_status', 'created_at', 'updated_at']