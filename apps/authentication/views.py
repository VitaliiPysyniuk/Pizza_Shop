from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny

from .seriazlizers import UserRegisterSerializer


class RegisterUserView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegisterSerializer




