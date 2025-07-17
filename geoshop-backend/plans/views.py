from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from .models import Plan, StoreSubscription
from .serializers import PlanSerializer, StoreSubscriptionSerializer
from django.shortcuts import get_object_or_404
import stripe
from django.conf import settings

class PlanListView(generics.ListAPIView):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [permissions.IsAuthenticated]

class StoreSubscriptionCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if request.user.user_type != 'store':
            return Response({"error": "Apenas lojas podem criar assinaturas"}, status=status.HTTP_403_FORBIDDEN)

        serializer = StoreSubscriptionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(store=request.user)
            return Response({"message": "Assinatura criada com sucesso", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProcessPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if request.user.user_type != 'store':
            return Response({"error": "Apenas lojas podem processar pagamentos"}, status=status.HTTP_403_FORBIDDEN)

        subscription_id = request.data.get('subscription_id')
        payment_method_id = request.data.get('payment_method_id')
        subscription = get_object_or_404(StoreSubscription, id=subscription_id, store=request.user)

        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            payment_intent = stripe.PaymentIntent.create(
                amount=int(subscription.plan.price * 100),  # Em centavos
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

                return Response({"message": "Pagamento concluído com sucesso, plano ativado"}, status=status.HTTP_200_OK)
            else:
                subscription.payment_status = 'failed'
                subscription.save()
                return Response({"error": "Falha no pagamento"}, status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.StripeError as e:
            subscription.payment_status = 'failed'
            subscription.save()
            return Response({"error": f"Erro no pagamento: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)