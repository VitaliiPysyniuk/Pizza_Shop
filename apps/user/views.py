from django.contrib.auth import get_user_model
from rest_framework.generics import ListCreateAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny

from .serializers import UserSerializer, UserFavoritesSerializer
from .models import UserFavoritesModel
from .permissions import IsManager

UserModel = get_user_model()


class UserCreateListView(ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsManager]
    queryset = UserModel.objects.all()
    serializer_class = UserSerializer


class CourierUpdateView(UpdateAPIView):
    permission_classes = [IsAuthenticated, IsManager]
    queryset = UserModel.objects.all()
    serializer_class = UserSerializer


class UserFavoritesListCreateView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = UserFavoritesModel.objects.all()
    serializer_class = UserFavoritesSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'user':
            return UserFavoritesModel.objects.filter(user_id=user.id)
        return UserFavoritesModel.objects.all()

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)


class UserFavoriteDeleteView(DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = UserFavoritesModel.objects.all()

