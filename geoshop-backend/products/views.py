from rest_framework import generics, permissions, status, serializers
from rest_framework.response import Response
from .models import Product, StoreProduct
from .serializers import ProductSerializer, StoreProductSerializer
from users.models import CustomUser
import logging

# Configurar logger
logger = logging.getLogger(__name__)

class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.user_type != 'admin':
            logger.warning(f"Usuário {self.request.user.username} tentou criar produto sem permissão de admin")
            raise permissions.PermissionDenied("Apenas administradores podem criar produtos.")
        serializer.save(admin=self.request.user)

class ProductRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        if self.request.user.user_type != 'admin':
            logger.warning(f"Usuário {self.request.user.username} tentou atualizar produto sem permissão de admin")
            raise permissions.PermissionDenied("Apenas administradores podem atualizar produtos.")
        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user.user_type != 'admin':
            logger.warning(f"Usuário {self.request.user.username} tentou excluir produto sem permissão de admin")
            raise permissions.PermissionDenied("Apenas administradores podem excluir produtos.")
        instance.delete()

class StoreProductListCreateView(generics.ListCreateAPIView):
    serializer_class = StoreProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        store_id = self.request.query_params.get('store_id')
        if self.request.user.user_type == 'store':
            return StoreProduct.objects.filter(store=self.request.user)
        elif self.request.user.user_type == 'admin' and store_id:
            try:
                return StoreProduct.objects.filter(store_id=store_id)
            except ValueError:
                return StoreProduct.objects.none()
        return StoreProduct.objects.all()

    def create(self, request, *args, **kwargs):
        logger.debug(f"Recebendo requisição POST com dados: {request.data}")
        try:
            serializer = self.get_serializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            logger.info(f"StoreProduct criado com sucesso: {serializer.data}")
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except serializers.ValidationError as e:
            logger.error(f"Erro de validação: {str(e)}")
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Erro inesperado ao criar StoreProduct: {str(e)}")
            return Response({"detail": f"Erro ao criar produto: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        if self.request.user.user_type != 'store':
            logger.warning(f"Usuário {self.request.user.username} tentou criar StoreProduct sem permissão de loja")
            raise permissions.PermissionDenied("Apenas lojas podem adicionar produtos.")
        
        if not self.request.user.active_plan:
            logger.warning(f"Usuário {self.request.user.username} tentou criar StoreProduct sem plano ativo")
            raise permissions.PermissionDenied("Nenhum plano ativo. Escolha um plano e conclua o pagamento primeiro.")
        
        product_count = StoreProduct.objects.filter(store=self.request.user).count()
        if product_count >= self.request.user.active_plan.product_limit:
            logger.warning(f"Usuário {self.request.user.username} atingiu limite de produtos: {product_count}")
            raise permissions.PermissionDenied(
                f"Limite de {self.request.user.active_plan.product_limit} produtos atingido para o plano {self.request.user.active_plan.get_name_display()}."
            )
        
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
            logger.warning(f"Usuário {self.request.user.username} tentou atualizar StoreProduct sem permissão de loja")
            raise permissions.PermissionDenied("Apenas lojas podem atualizar seus produtos.")
        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user.user_type != 'store' or instance.store != self.request.user:
            logger.warning(f"Usuário {self.request.user.username} tentou excluir StoreProduct sem permissão")
            raise permissions.PermissionDenied("Apenas lojas podem excluir seus produtos.")
        instance.delete()