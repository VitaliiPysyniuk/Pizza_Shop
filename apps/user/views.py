from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from rest_framework.generics import ListCreateAPIView, DestroyAPIView, RetrieveUpdateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated

from .serializers import UserSerializer, UserFavoritesSerializer
from .models import UserFavoritesModel
from .permissions import IsManager

UserModel = get_user_model()


@extend_schema_view(
    get=extend_schema(
        summary='Get list of all users.',
        description='Receives list of all users regardless of the user role. Only manager can do this.'
    ),
    post=extend_schema(
        summary='Create new courier.',
        description='Create a new courier, a simple user is created via auth api. Only manager can do this.'
    )
)
class UserCreateListView(ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsManager]
    queryset = UserModel.objects.all()
    serializer_class = UserSerializer


@extend_schema_view(
    get=extend_schema(
        summary='Get the specific user.',
        description='User is selected by a set parameter user_id.',
        parameters=[OpenApiParameter(name='user_id', type=int, required=True, location='path',
                                     description='The id of the specific user.')]
    ),
    patch=extend_schema(
        summary='Update the specific user.',
        description='User is selected by a set parameter user_id. The manager can change all fields of the user info, '
                    'the user can change all fields except field role and field is_active.',
        parameters=[OpenApiParameter(name='user_id', type=int, required=True, location='path',
                                     description='The id of the specific user.')]
    ),
    put=extend_schema(exclude=True)
)
class UserRetrieveUpdateView(RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    queryset = UserModel.objects.all()

    def get_permissions(self):
        keys = self.request.data.keys()
        if ('role' in keys) or ('is_active' in keys):
            return [IsAuthenticated(), IsManager()]
        return [IsAuthenticated()]

    def get_object(self):
        lookup_kwargs = {
            'id': self.kwargs.get('user_id')
        }
        return self.get_queryset().get(**lookup_kwargs)


@extend_schema_view(
    get=extend_schema(
        summary="Get the list of favorite pizzas of all users.",
        description="Get the list of favorite pizzas of all users. Only manager can do this."
    )
)
class UserFavoritesListView(ListAPIView):
    permission_classes = [IsAuthenticated, IsManager]
    queryset = UserFavoritesModel.objects.all()
    serializer_class = UserFavoritesSerializer

    def get_queryset(self):
        queryset = UserFavoritesModel.objects.filter(user__role='user')
        return queryset


@extend_schema_view(
    get=extend_schema(
        summary="Get the list of favorite pizzas of the specific user.",
        description="Get the list of favorite pizzas of the specific user. User is selected by a set parameter user_id.",
        parameters=[
            OpenApiParameter(name='user_id', type=int, required=True, location='path',
                             description='The id of the specific user.')
        ]
    ),
    post=extend_schema(
        summary="Add new pizza to the list of favorite pizzas of the specific user.",
        description="Add new pizza to the list of favorite pizzas of the specific user. User is selected by a set "
                    "parameter user_id.",
        parameters=[
            OpenApiParameter(name='user_id', type=int, required=True, location='path',
                             description='The id of the specific user.')
        ]
    )
)
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
        user_id = self.kwargs.get('user_id')
        serializer.save(user_id=user_id)


@extend_schema_view(
    delete=extend_schema(
        summary="Delete pizza from user's favorite list.",
        description="Delete pizza from user's favorite list. User is selected by a set parameter user_id. "
                    "the item from favorite pizza list is selected by a set parameter favorite_id.",
        parameters=[
            OpenApiParameter(name='user_id', type=int, required=True, location='path',
                             description='The id of the specific user.'),
            OpenApiParameter(name='favorite_id', type=int, required=True, location='path',
                             description='The id of the specific item from the favorite pizza list.'),
        ]
    ),
)
class UserFavoriteDeleteView(DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = UserFavoritesModel.objects.all()
    serializer_class = UserFavoritesSerializer

    def get_object(self):
        lookup_kwargs = {
            'user_id': self.kwargs.get('user_id'),
            'id': self.kwargs.get('favorite_id')
        }
        return self.get_queryset().get(**lookup_kwargs)
