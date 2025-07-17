from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Plan, StoreSubscription
from .serializers import PlanSerializer, StoreSubscriptionSerializer
from django.shortcuts import get_object_or_404
import stripe
from django.conf import settings

class PlanListCreateView(generics.ListCreateAPIView):
    serializer_class = PlanSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Admin vê todos, outros usuários só vêem ativos
        if self.request.user.is_staff:
            return Plan.objects.all()
        return Plan.objects.filter(ativo=True)

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAdminUser()]  # Apenas admins podem criar

class PlanDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PlanSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Plan.objects.all()
        return Plan.objects.filter(ativo=True)

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAdminUser()]  # Apenas admins podem atualizar/excluir


class StoreSubscriptionCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.user_type != 'store':
            return Response({"error": "Apenas lojas podem ver assinaturas"}, status=status.HTTP_403_FORBIDDEN)
        
        subscriptions = StoreSubscription.objects.filter(store=request.user)
        serializer = StoreSubscriptionSerializer(subscriptions, many=True)
        return Response(serializer.data)

    def post(self, request):
        if request.user.user_type != 'store':
            return Response({"error": "Apenas lojas podem criar assinaturas"}, status=status.HTTP_403_FORBIDDEN)

        serializer = StoreSubscriptionSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(store=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProcessPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.user_type != 'store':
            return Response({"error": "Apenas lojas podem processar pagamentos"}, status=status.HTTP_403_FORBIDDEN)

        subscription_id = request.data.get('subscription_id')
        payment_method_id = request.data.get('payment_method_id')
        
        try:
            subscription = StoreSubscription.objects.get(id=subscription_id, store=request.user)
        except StoreSubscription.DoesNotExist:
            return Response({"error": "Assinatura não encontrada"}, status=status.HTTP_404_NOT_FOUND)

        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            payment_intent = stripe.PaymentIntent.create(
                amount=int(subscription.plan.price * 100),
                currency='brl',
                payment_method=payment_method_id,
                confirm=True,
                metadata={'subscription_id': subscription.id}
            )

            if payment_intent.status == 'succeeded':
                subscription.is_active = True
                subscription.payment_status = 'completed'
                subscription.save()

                request.user.active_plan = subscription.plan
                request.user.save()

                return Response({"message": "Pagamento concluído com sucesso"}, status=status.HTTP_200_OK)
            else:
                subscription.payment_status = 'failed'
                subscription.save()
                return Response({"error": "Falha no pagamento"}, status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.StripeError as e:
            subscription.payment_status = 'failed'
            subscription.save()
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)