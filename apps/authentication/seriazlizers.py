from rest_framework.serializers import ModelSerializer
from django.contrib.auth import get_user_model

UserModel = get_user_model()


class UserRegisterSerializer(ModelSerializer):
    class Meta:
        model = UserModel
        exclude = ['id', 'role', 'is_active']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        return UserModel.objects.create_user(**validated_data)

