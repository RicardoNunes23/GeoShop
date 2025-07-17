from django.urls import path
from .views import PlanListCreateView, PlanDetailView, StoreSubscriptionCreateView, ProcessPaymentView

urlpatterns = [
    path('plans/', PlanListCreateView.as_view(), name='plan-list-create'),
    path('plans/<int:pk>/', PlanDetailView.as_view(), name='plan-detail'),
    path('store/subscription/', StoreSubscriptionCreateView.as_view(), name='store-subscription-create'),
    path('store/process-payment/', ProcessPaymentView.as_view(), name='process-payment'),
]