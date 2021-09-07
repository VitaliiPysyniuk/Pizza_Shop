from django.urls import reverse
from django.test import TestCase

from ..models import CustomUserModel


class TestUserModels(TestCase):
    def setUp(self):
        self.user_data = {'email': 'user@gmail.com', 'password': 'user', 'first_name': 'Petro', 'last_name': 'Petrov',
                          'phone_number': '38098878344730', 'is_active': True}
        self.manager_data = {'email': 'admin@gmail.com', 'password': 'admin', 'first_name': 'Admin',
                             'last_name': 'Admin', 'phone_number': '38098878306930'}

    def test_user_creation_without_email(self):
        self.user_data.pop('email')

        with self.assertRaises(TypeError):
            CustomUserModel.objects.create_user(**self.user_data)

    def test_manager_creation_with_wrong_role(self):
        self.manager_data['role'] = 'courier'

        with self.assertRaisesMessage(ValueError, "User role has to be 'manager'."):
            CustomUserModel.objects.create_superuser(**self.manager_data)

    def test_manager_creation_with_wrong_active_status(self):
        self.manager_data['is_active'] = False

        with self.assertRaisesMessage(ValueError, 'User has to be active.'):
            CustomUserModel.objects.create_superuser(**self.manager_data)

