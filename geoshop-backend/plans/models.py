from django.db import models
from users.models import CustomUser

class Plan(models.Model):
    PLAN_TYPES = (
        ('A', 'Plano A - Grátis'),
        ('B', 'Plano B'),
        ('C', 'Plano C'),
        ('D', 'Plano D'),
        ('E', 'Plano E'),
    )

    name = models.CharField(max_length=1, choices=PLAN_TYPES, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    product_limit = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.get_name_display()} - R${self.price} - {self.product_limit} produtos"

class StoreSubscription(models.Model):
    store = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        limit_choices_to={'user_type': 'store'}
    )
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)  # Ativado após pagamento
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    payment_status = models.CharField(
        max_length=20,
        choices=(
            ('pending', 'Pendente'),
            ('completed', 'Concluído'),
            ('failed', 'Falhou'),
        ),
        default='pending'
    )

    def __str__(self):
        return f"{self.store.username} - {self.plan.get_name_display()} ({self.payment_status})"