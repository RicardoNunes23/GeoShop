from django.urls import path
from .views import (
    ProductListCreateView, ProductRetrieveUpdateDestroyView,
    StoreProductListCreateView, StoreProductRetrieveUpdateDestroyView,
    ClientCartListCreateView, ClientCartRetrieveUpdateDestroyView,
    CartItemCreateView, CartItemRetrieveUpdateDestroyView,
    BestStoreForCartView
)

urlpatterns = [
    path('products/', ProductListCreateView.as_view(), name='product-list'),
    path('products/<int:pk>/', ProductRetrieveUpdateDestroyView.as_view(), name='product-detail'),
    path('store-products/', StoreProductListCreateView.as_view(), name='store-product-list'),
    path('store-products/<int:pk>/', StoreProductRetrieveUpdateDestroyView.as_view(), name='store-product-detail'),
    path('carts/', ClientCartListCreateView.as_view(), name='cart-list'),
    path('carts/<int:pk>/', ClientCartRetrieveUpdateDestroyView.as_view(), name='cart-detail'),
    path('carts/<int:cart_id>/items/', CartItemCreateView.as_view(), name='cart-item-create'),
    path('cart-items/<int:pk>/', CartItemRetrieveUpdateDestroyView.as_view(), name='cart-item-detail'),
    path('carts/<int:pk>/best-store/', BestStoreForCartView.as_view(), name='best-store'),
]