from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from .managers import CustomUserManager
from ..pizza.models import PizzaSizeModel


class CustomUserModel(AbstractBaseUser, PermissionsMixin):
    class Meta:
        db_table = 'users'

    email = models.EmailField(unique=True)
    password = models.CharField(max_length=200)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=14, unique=True)
    role = models.CharField(max_length=7, default='user')
    is_active = models.BooleanField(default=False)
    creation_time = models.DateTimeField(auto_now_add=True)

    last_login = None
    is_superuser = None
    groups = None
    user_permissions = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()


class UserFavoritesModel(models.Model):
    class Meta:
        db_table = 'user_favorites'

    user = models.ForeignKey(CustomUserModel, on_delete=models.CASCADE, related_name='favorite_pizzas')
    pizza_size = models.ForeignKey(PizzaSizeModel, on_delete=models.CASCADE)
