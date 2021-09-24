from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiExample, OpenApiParameter
from rest_framework import status
from rest_framework.generics import CreateAPIView, GenericAPIView, get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .seriazlizers import UserRegisterSerializer
from ..user.models import CustomUserModel


@extend_schema_view(
    post=extend_schema(
        summary='Registers new user.',
        description='Create a new inactive user profile from user data. When creating a user, an activation link comes '
                    'to his e-mail.',
    )
)
class UserRegisterView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegisterSerializer


@extend_schema_view(
    get=extend_schema(exclude=True)
)
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
        serializer = UserRegisterSerializer(user=user)

        return Response(serializer.data, status.HTTP_200_OK)


@extend_schema_view(
    post=extend_schema(
        summary='Obtains access and refresh JSON web token pair.',
        description='Takes a set of user credentials and returns an access and refresh JSON web token pair to prove '
                    'the authentication of those credentials.',
    )
)
class TokenObtainPairViewCustom(TokenObtainPairView):
    pass


@extend_schema_view(
    post=extend_schema(
        summary='Refresh expired user access JSON web token.',
        description='Takes a refresh type JSON web token and returns an access type JSON web token if the refresh '
                    'token is valid.',
    )
)
class TokenRefreshViewCustom(TokenRefreshView):
    pass
