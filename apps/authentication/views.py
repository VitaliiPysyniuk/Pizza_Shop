from rest_framework import status
from rest_framework.generics import CreateAPIView, GenericAPIView, get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .seriazlizers import UserRegisterSerializer
from ..user.models import CustomUserModel


class UserRegisterView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegisterSerializer


class UserActivateView(GenericAPIView):
    permission_classes = [AllowAny]

    def get(self, *args, **kwargs):
        token = self.request.query_params.get('token')
        try:
            token = RefreshToken(token)
            user_id = token.payload.get('user_id')
            token.blacklist()
        except TokenError as err:
            return Response({'error': str(err)}, status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(CustomUserModel, pk=user_id)
        user.is_active = True
        user.save()
        serializer = UserRegisterSerializer(user)
        return Response(serializer.data, status.HTTP_200_OK)




