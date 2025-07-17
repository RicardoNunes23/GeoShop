from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Product, StoreProduct, ClientCart, CartItem
from .serializers import ProductSerializer, StoreProductSerializer, ClientCartSerializer, CartItemSerializer
from users.models import CustomUser
from django.shortcuts import get_object_or_404

class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.user_type != 'admin':
            raise permissions.PermissionDenied("Apenas administradores podem criar produtos.")
        serializer.save(admin=self.request.user)

class ProductRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        if self.request.user.user_type != 'admin':
            raise permissions.PermissionDenied("Apenas administradores podem atualizar produtos.")
        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user.user_type != 'admin':
            raise permissions.PermissionDenied("Apenas administradores podem excluir produtos.")
        instance.delete()

class StoreProductListCreateView(generics.ListCreateAPIView):
    serializer_class = StoreProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Obtém o parâmetro store_id da query
        store_id = self.request.query_params.get('store_id')
        
        if self.request.user.user_type == 'store':
            # Lojas só podem ver seus próprios produtos
            return StoreProduct.objects.filter(store=self.request.user)
        elif self.request.user.user_type == 'admin' and store_id:
            # Administradores podem filtrar por store_id
            try:
                return StoreProduct.objects.filter(store_id=store_id)
            except ValueError:
                return StoreProduct.objects.none()  # Retorna vazio se store_id for inválido
        return StoreProduct.objects.all()  # Administradores sem store_id veem todos os produtos

    def perform_create(self, serializer):
        if self.request.user.user_type != 'store':
            raise permissions.PermissionDenied("Apenas lojas podem adicionar produtos.")
        serializer.save(store=self.request.user)

class StoreProductRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StoreProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.user_type == 'store':
            return StoreProduct.objects.filter(store=self.request.user)
        return StoreProduct.objects.all()

    def perform_update(self, serializer):
        if self.request.user.user_type != 'store':
            raise permissions.PermissionDenied("Apenas lojas podem atualizar seus produtos.")
        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user.user_type != 'store' or instance.store != self.request.user:
            raise permissions.PermissionDenied("Apenas lojas podem excluir seus produtos.")
        instance.delete()

class ClientCartListCreateView(generics.ListCreateAPIView):
    serializer_class = ClientCartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.user_type == 'client':
            return ClientCart.objects.filter(client=self.request.user)
        return ClientCart.objects.none()  # Retorna queryset vazio para não-clientes

    def perform_create(self, serializer):
        if self.request.user.user_type != 'client':
            raise permissions.PermissionDenied("Apenas clientes podem criar carrinhos.")
        serializer.save(client=self.request.user)

class ClientCartRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ClientCartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.user_type == 'client':
            return ClientCart.objects.filter(client=self.request.user)
        return ClientCart.objects.none()

    def perform_update(self, serializer):
        if self.request.user.user_type != 'client' or serializer.instance.client != self.request.user:
            raise permissions.PermissionDenied("Apenas o dono do carrinho pode atualizá-lo.")
        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user.user_type != 'client' or instance.client != self.request.user:
            raise permissions.PermissionDenied("Apenas o dono do carrinho pode excluí-lo.")
        instance.delete()

class CartItemCreateView(generics.CreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Verifica se o usuário é cliente
        if self.request.user.user_type != 'client':
            raise permissions.PermissionDenied("Apenas clientes podem adicionar itens ao carrinho.")
        
        # Obtém ou cria um carrinho ativo para o cliente
        cart, created = ClientCart.objects.get_or_create(
            client=self.request.user,
            is_completed=False
        )
        
        # Salva o item no carrinho
        serializer.save(cart=cart)

class CartItemRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.user_type == 'client':
            return CartItem.objects.filter(cart__client=self.request.user)
        return CartItem.objects.none()

    def perform_update(self, serializer):
        if self.request.user.user_type != 'client' or serializer.instance.cart.client != self.request.user:
            raise permissions.PermissionDenied("Apenas o dono do carrinho pode atualizar itens.")
        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user.user_type != 'client' or instance.cart.client != self.request.user:
            raise permissions.PermissionDenied("Apenas o dono do carrinho pode remover itens.")
        instance.delete()

class BestStoreForCartView(generics.RetrieveAPIView):
    serializer_class = ClientCartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.user_type == 'client':
            return ClientCart.objects.filter(client=self.request.user)
        return ClientCart.objects.none()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        best_store = serializer.get_best_store(instance)
        
        if not best_store:
            return Response({"detail": "Nenhuma loja encontrada para os itens no carrinho."}, 
                           status=status.HTTP_404_NOT_FOUND)
        
        return Response(best_store)