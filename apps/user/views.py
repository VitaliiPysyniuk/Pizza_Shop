from django.contrib.auth import get_user_model
from rest_framework.generics import ListCreateAPIView, DestroyAPIView, RetrieveUpdateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated

from .serializers import UserSerializer, UserFavoritesSerializer
from .models import UserFavoritesModel
from .permissions import IsManager

UserModel = get_user_model()


class UserCreateListView(ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsManager]
    queryset = UserModel.objects.all()
    serializer_class = UserSerializer


class UserRetrieveUpdateView(RetrieveUpdateAPIView):
    queryset = UserModel.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        keys = self.request.data.keys()
        if ('role' in keys) or ('is_active' in keys):
            return [IsAuthenticated(), IsManager()]
        return [IsAuthenticated()]


class UserFavoritesListView(ListAPIView):
    permission_classes = [IsAuthenticated, IsManager]
    queryset = UserFavoritesModel.objects.all()
    serializer_class = UserFavoritesSerializer


class UserFavoritesListCreateView(ListCreateAPIView):
    serializer_class = UserFavoritesSerializer

    def get_permissions(self):
        user = self.request.user
        user_id = self.kwargs.get('user_id')
        if user.id == user_id:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsManager()]

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        queryset = UserFavoritesModel.objects.filter(user_id=user_id)
        return queryset

    def perform_create(self, serializer):
        print(self.request.data)
        user_id = self.kwargs.get('user_id')
        serializer.save(user_id=user_id)


class UserFavoriteDeleteView(DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        pk = self.kwargs.get('pk')
        queryset = UserFavoritesModel.objects.filter(pk=pk)
        return queryset





