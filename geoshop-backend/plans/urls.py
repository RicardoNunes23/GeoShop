from django.urls import path
from .views import PlanListView, StoreSubscriptionCreateView, ProcessPaymentView

urlpatterns = [
    path('plans/', PlanListView.as_view(), name='plan-list'),
    path('store/subscription/', StoreSubscriptionCreateView.as_view(), name='store-subscription-create'),
    path('store/process-payment/', ProcessPaymentView.as_view(), name='process-payment'),
]