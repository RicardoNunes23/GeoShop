from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .serializers import ClientRegisterSerializer, StoreRegisterSerializer, StoreUpdateSerializer, UserSerializer
from .models import CustomUser
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser

class UserListView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        return CustomUser.objects.all()

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = StoreUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Apenas administradores ou o próprio usuário podem acessar/atualizar/deletar
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return CustomUser.objects.all()
        return CustomUser.objects.filter(id=user.id)

    def perform_update(self, serializer):
        # Garante que apenas campos permitidos sejam atualizados
        serializer.save()

    def perform_destroy(self, instance):
        # Adiciona verificação extra antes de deletar
        if self.request.user.is_staff or self.request.user.id == instance.id:
            instance.delete()
        else:
            raise permissions.PermissionDenied("Você não tem permissão para excluir este usuário.")

class CustomTokenObtainPairView(APIView):
    def post(self, request):
        serializer = TokenObtainPairSerializer(data={
            'username': request.data.get('username'),
            'password': request.data.get('password')
        })
        if serializer.is_valid():
            user = CustomUser.objects.get(username=request.data.get('username'))
            data = serializer.validated_data
            data['user'] = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'user_type': user.user_type,
                'phone': user.phone,
            }
            return Response(data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ClientRegisterView(APIView):
    def post(self, request):
        serializer = ClientRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Cliente registrado com sucesso"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class StoreRegisterView(APIView):
    def post(self, request):
        serializer = StoreRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Loja registrada com sucesso"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class StoreProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.user_type != 'store':
            return Response({"error": "Acesso negado"}, status=status.HTTP_403_FORBIDDEN)
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        if request.user.user_type != 'store':
            return Response({"error": "Acesso negado"}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = StoreUpdateSerializer(
            request.user, 
            data=request.data, 
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Perfil atualizado com sucesso",
                "data": serializer.data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        if request.user.user_type != 'store':
            return Response({"error": "Acesso negado"}, status=status.HTTP_403_FORBIDDEN)
        request.user.delete()
        return Response({"message": "Perfil excluído com sucesso"}, status=status.HTTP_204_NO_CONTENT)