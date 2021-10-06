# from rest_framework.test import APITestCase
# from django.urls import reverse
# from rest_framework import status
# from django.contrib.auth import get_user_model
# from rest_framework_simplejwt.tokens import RefreshToken
#
# from ..services import Email
# from ..views import UserSerializer
#
# UserModel = get_user_model()
#
#
# class TestAuthenticationViews(APITestCase):
#
#     def setUp(self):
#         self.user_1_data = {'email': 'user1@gmail.com', 'password': 'user1@gmail.com', 'first_name': 'Petro',
#                             'last_name': 'Petrov', 'phone_number': '38098878344730'}
#         self.user_2_data = {'email': 'user2@gmail.com', 'password': 'user2@gmail.com', 'first_name': 'Oleg',
#                             'last_name': 'Olegov', 'phone_number': '38093378344730', 'is_active': True}
#         self.inactive_user = UserModel.objects.create_user(**self.user_1_data)
#         self.register_url = reverse('register_new_user')
#         self.login_url = reverse('obtain_token_pair')
#         self.activate_url = reverse('activate_new_user')
#
#     def test_user_registration_with_valid_email_and_phone_number(self):
#         count_of_users_before_adding = UserModel.objects.all().count()
#         response = self.client.post(self.register_url, self.user_2_data)
#
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(UserModel.objects.all().count(), count_of_users_before_adding + 1)
#
#     def test_user_registration_with_invalid_email(self):
#         self.user_1_data['phone_number'] = '38091479844730'
#         count_of_users_before_adding = UserModel.objects.all().count()
#         response = self.client.post(self.register_url, self.user_1_data)
#
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(response.data['email'][0], 'custom user model with this email already exists.')
#         self.assertEqual(UserModel.objects.all().count(), count_of_users_before_adding)
#
#     def test_user_registration_with_invalid_phone_number(self):
#         self.user_1_data['email'] = 'user2@gmail.com'
#         count_of_users_before_adding = UserModel.objects.all().count()
#         response = self.client.post(self.register_url, self.user_1_data)
#
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(response.data['phone_number'][0], 'custom user model with this phone number already exists.')
#         self.assertEqual(UserModel.objects.all().count(), count_of_users_before_adding)
#
#     def test_user_activation_with_valid_token(self):
#         token = Email.create_email_token(self.inactive_user)
#         self.activate_url += f'?token={token}'
#         response = self.client.get(self.activate_url)
#
#         activated_user = UserModel.objects.filter(email=response.data['email'])
#         activated_user_data = UserSerializer(instance=activated_user, many=True).data[0]
#
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['email'], self.user_1_data.get('email'))
#         self.assertEqual(activated_user_data.get('is_active'), True)
#
#     def test_user_activation_with_invalid_token(self):
#         token = Email.create_email_token(self.inactive_user)
#         self.activate_url += f'?token={token}'
#         token = RefreshToken(str(token))
#         token.blacklist()
#         response = self.client.get(self.activate_url)
#
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(response.data['error'], 'Token is blacklisted')
#
#
#
#
#
