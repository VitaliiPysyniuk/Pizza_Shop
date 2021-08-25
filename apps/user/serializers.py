from rest_framework.serializers import ModelSerializer
from django.contrib.auth import get_user_model

from .models import UserFavoritesModel

UserModel = get_user_model()


class UserSerializer(ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['id', 'email', 'password', 'first_name', 'last_name', 'phone_number', 'role', 'is_active']

    def create(self, validated_data):
        return UserModel.objects.create_user(**validated_data)


class UserFavoritesSerializer(ModelSerializer):
    class Meta:
        model = UserFavoritesModel
        fields = ['id', 'user', 'pizza_size']
        extra_kwargs = {'user': {'required': False}}





