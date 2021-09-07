from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status

from ..views import CustomUserModel


class TestAuthenticationViews(APITestCase):

    def setUp(self):
        self.user_1_data = {'email': 'user1@gmail.com', 'password': 'user1@gmail.com', 'first_name': 'Petro',
                            'last_name': 'Petrov', 'phone_number': '38098878344730'}
        self.user_2_data = {'email': 'user2@gmail.com', 'password': 'user2@gmail.com', 'first_name': 'Oleg',
                            'last_name': 'Olegov', 'phone_number': '38093378344730', 'is_active': True}
        self.inactive_user = CustomUserModel.objects.create_user(**self.user_1_data)
        self.register_url = reverse('register_new_user')
        self.login_url = reverse('obtain_token_pair')

    def test_user_registration_with_valid_email_and_phone_number(self):
        count_of_users_before_adding = CustomUserModel.objects.all().count()
        response = self.client.post(self.register_url, self.user_2_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomUserModel.objects.all().count(), count_of_users_before_adding + 1)

    def test_user_registration_with_invalid_email(self):
        self.user_1_data['phone_number'] = '38091479844730'
        count_of_users_before_adding = CustomUserModel.objects.all().count()
        response = self.client.post(self.register_url, self.user_1_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['email'][0], 'custom user model with this email already exists.')
        self.assertEqual(CustomUserModel.objects.all().count(), count_of_users_before_adding)

    def test_user_registration_with_invalid_phone_number(self):
        self.user_1_data['email'] = 'user2@gmail.com'
        count_of_users_before_adding = CustomUserModel.objects.all().count()
        response = self.client.post(self.register_url, self.user_1_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['phone_number'][0], 'custom user model with this phone number already exists.')
        self.assertEqual(CustomUserModel.objects.all().count(), count_of_users_before_adding)




