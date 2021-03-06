from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model

from ..serializers import UserSerializer

UserModel = get_user_model()

class TestUserViews(APITestCase):

    def setUp(self):
        self.user_data = {'email': 'user@gmail.com', 'password': 'user', 'first_name': 'Petro', 'last_name': 'Petrov',
                          'phone_number': '38077878344730', 'is_active': True}
        self.manager_data = {'email': 'admin@gmail.com', 'password': 'admin', 'first_name': 'Admin',
                             'last_name': 'Admin', 'phone_number': '38098878306930'}
        self.courier_data = {'email': 'courier@gmail.com', 'password': 'courier', 'first_name': 'Andriy',
                             'last_name': 'Bilous', 'phone_number': '38097741494730', 'is_active': True,
                             'role': 'courier'}
        self.user = UserModel.objects.create_user(**self.user_data)
        self.manager = UserModel.objects.create_superuser(**self.manager_data)

        self.get_all_url = reverse('get_all_registered_users')
        # self.get_update_single_url = reverse('get_update_user_information')
        # self.get_all_favorites_url = reverse('get_favorites_of_all_users')
        # self.get_create_favorite_url = reverse('get_create_user_favorites')
        # self.delete_favorite_url = reverse('delete_user_favorite')
        self.login_url = reverse('obtain_token_pair')

    def user_authentication(self):
        response = self.client.post(self.login_url, {"email": self.user_data['email'],
                                                     "password": self.user_data['password']})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

    def manager_authentication(self):
        response = self.client.post(self.login_url, {"email": self.manager_data['email'],
                                                     "password": self.manager_data['password']})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

    # def test_getting_all_users_with_manager_credentials(self):
    #     self.manager_authentication()
    #     response = self.client.get(self.get_all_url)
    #
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertIsInstance(response.data, list)
    #
    # def test_getting_all_users_without_manager_credentials(self):
    #     self.user_authentication()
    #     response = self.client.get(self.get_all_url)
    #
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #     self.assertNotIsInstance(response.data, list)
    #
    # def test_creating_new_courier(self):
    #     self.manager_authentication()
    #     count_of_users_before_creating = UserModel.objects.all().count()
    #     response = self.client.post(self.get_all_url, self.courier_data)
    #
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     self.assertEqual(UserModel.objects.all().count(), count_of_users_before_creating + 1)
    #     self.assertEqual(response.data['role'], 'courier')
    #
    # def test_manager_getting_single_user_by_id(self):
    #     self.manager_authentication()
    #     url = reverse('get_update_user_information', kwargs={'user_id': self.user.id})
    #     response = self.client.get(url)
    #
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data['email'], self.user.email)
    #     self.assertEqual(response.data['phone_number'], self.user.phone_number)

    def test_user_update_role_by_manager(self):
        self.manager_authentication()
        url = reverse('get_update_user_information', kwargs={'user_id': self.user.id})
        response = self.client.patch(url, {'role': 'courier'})

        updated_user = UserModel.objects.filter(id=response.data['id'])
        updated_user_data = UserSerializer(updated_user, many=True).data[0]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['role'], 'courier')
        self.assertEqual(updated_user_data.get('role'), 'courier')

    def test_user_update_role_by_simple_user(self):
        self.user_authentication()
        url = reverse('get_update_user_information', kwargs={'user_id': self.user.id})
        response = self.client.patch(url, {'role': 'courier'})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_update_profile_by_simple_user(self):
        self.user_authentication()
        url = reverse('get_update_user_information', kwargs={'user_id': self.user.id})
        response = self.client.patch(url, {'phone_number': '38077811144730'})

        updated_user = UserModel.objects.filter(id=response.data['id'])
        updated_user_data = UserSerializer(updated_user, many=True).data[0]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['phone_number'], '38077811144730')
        self.assertEqual(updated_user_data.get('phone_number'), '38077811144730')

