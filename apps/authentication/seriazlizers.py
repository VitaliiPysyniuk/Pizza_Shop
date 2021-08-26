from rest_framework.serializers import ModelSerializer
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from .services import Email

UserModel = get_user_model()


class UserRegisterSerializer(ModelSerializer):
    class Meta:
        model = UserModel
        exclude = ['id', 'role', 'is_active']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = UserModel.objects.create_user(**validated_data)
        token = Email.create_email_token(user)
        data = {
            'subject': 'Account activation from Pizza shop',
            'body': f'Dear, {user.first_name} {user.last_name}.\n'
                    f'Tap on this link to activate your account.\n'
                    f'Link: http://localhost:8000/api/v1/auth/activate?token={token}',
            'to': [user.email]
        }
        Email.send_email(**data)
        return user

