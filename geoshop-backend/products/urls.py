from django.urls import path
from .views import (
    ProductListCreateView,
    ProductRetrieveUpdateDestroyView,
    StoreProductListCreateView,
    StoreProductRetrieveUpdateDestroyView,
    ClientProductSearchView,
    ClientStoreProductListView,
    ClientShoppingListView,
)

urlpatterns = [
    path('products/', ProductListCreateView.as_view(), name='product-list'),
    path('products/<int:pk>/', ProductRetrieveUpdateDestroyView.as_view(), name='product-detail'),
    path('store-products/', StoreProductListCreateView.as_view(), name='store-product-list'),
    path('store-products/<int:pk>/', StoreProductRetrieveUpdateDestroyView.as_view(), name='store-product-detail'),
    path('client/products/search/', ClientProductSearchView.as_view(), name='client-product-search'),
    path('client/store-products/<int:product_id>/', ClientStoreProductListView.as_view(), name='client-store-product-list'),
    path('client/shopping-list/', ClientShoppingListView.as_view(), name='client-shopping-list'),
]