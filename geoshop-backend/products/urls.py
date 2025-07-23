from django.urls import path
from .views import (
    ProductListCreateView, ProductRetrieveUpdateDestroyView,
    StoreProductListCreateView, StoreProductRetrieveUpdateDestroyView,
)

urlpatterns = [
    path('products/', ProductListCreateView.as_view(), name='product-list'),
    path('products/<int:pk>/', ProductRetrieveUpdateDestroyView.as_view(), name='product-detail'),
    path('store-products/', StoreProductListCreateView.as_view(), name='store-product-list'),
    path('store-products/<int:pk>/', StoreProductRetrieveUpdateDestroyView.as_view(), name='store-product-detail'),
]