from django.contrib.auth import get_user_model
from rest_framework.generics import ListCreateAPIView, UpdateAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated

from .serializers import UserSerializer
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








