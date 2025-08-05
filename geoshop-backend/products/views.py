# views.py
from rest_framework import generics, permissions, status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Product, StoreProduct
from .serializers import ProductSerializer, StoreProductSerializer, ShoppingListResultSerializer
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

class ClientProductSearchView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.user_type != 'client':
            logger.warning(f"Usuário {self.request.user.username} tentou buscar produtos sem permissão de cliente")
            raise permissions.PermissionDenied("Apenas clientes podem buscar produtos.")
        
        queryset = Product.objects.all()
        search_query = self.request.query_params.get('q', None)
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)
            logger.debug(f"Filtrando produtos com query: {search_query}")
        return queryset.order_by('name')

class ClientStoreProductListView(generics.ListAPIView):
    serializer_class = StoreProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.user_type != 'client':
            logger.warning(f"Usuário {self.request.user.username} tentou listar StoreProducts sem permissão de cliente")
            raise permissions.PermissionDenied("Apenas clientes podem listar produtos de lojas.")
        
        product_id = self.kwargs.get('product_id')
        if not product_id:
            logger.error("ID do produto não fornecido")
            raise serializers.ValidationError("ID do produto é obrigatório.")
        
        if not Product.objects.filter(id=product_id).exists():
            logger.error(f"Produto com ID {product_id} não encontrado")
            raise serializers.ValidationError("Produto não encontrado.")
        
        queryset = StoreProduct.objects.filter(product_id=product_id, is_active=True)
        return queryset.order_by('price')

class ClientShoppingListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        logger.debug(f"Recebida requisição para lista de compras: {request.data}")
        if self.request.user.user_type != 'client':
            logger.error(f"Usuário {self.request.user.username} não é cliente")
            return Response({"detail": "Apenas clientes podem acessar esta funcionalidade"}, status=status.HTTP_403_FORBIDDEN)

        items = request.data.get('items', [])
        if not items:
            logger.error("Nenhum item fornecido na lista de compras")
            return Response({"detail": "A lista de compras não pode estar vazia"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Agrupar StoreProducts por loja
            store_totals = {}
            for item in items:
                product_id = item.get('product_id')
                quantity = item.get('quantity')
                if not product_id or not isinstance(quantity, (int, float)) or quantity <= 0:
                    logger.error(f"Item inválido: product_id={product_id}, quantity={quantity}")
                    return Response({"detail": "Todos os itens devem ter product_id e quantity válidos"}, status=status.HTTP_400_BAD_REQUEST)

                # Buscar StoreProducts ativos para o produto
                store_products = StoreProduct.objects.filter(
                    product_id=product_id,
                    is_active=True
                ).select_related('store', 'product')

                for store_product in store_products:
                    store_id = store_product.store_id
                    if store_id not in store_totals:
                        store_totals[store_id] = {
                            'store_id': store_id,
                            'store_username': store_product.store.username,
                            'total_price': 0,
                            'items': [],
                            'store_latitude': store_product.store.latitude,
                            'store_longitude': store_product.store.longitude
                        }

                    # Calcular preço do item
                    price = store_product.price
                    if store_product.bulk_price and store_product.bulk_min_quantity and quantity >= store_product.bulk_min_quantity:
                        price = store_product.bulk_price
                    elif store_product.loyalty_price and request.user.has_loyalty_card:
                        price = store_product.loyalty_price

                    item_total = price * quantity
                    store_totals[store_id]['total_price'] += item_total
                    store_totals[store_id]['items'].append({
                        'store_product': store_product,
                        'quantity': quantity,
                        'item_total': item_total
                    })

            # Converter para lista
            result = list(store_totals.values())
            
            # Ordenar por preço total
            result.sort(key=lambda x: x['total_price'])

            # Serializar a resposta
            serializer = ShoppingListResultSerializer(result, many=True)
            logger.info(f"Lista de compras processada com sucesso: {len(result)} lojas encontradas")
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Erro ao processar lista de compras: {str(e)}")
            return Response({"detail": f"Erro ao processar lista de compras: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)