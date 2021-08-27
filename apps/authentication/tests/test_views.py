from rest_framework.test import APITestCase
from django.urls import reverse
from datetime import datetime
from rest_framework import status


class TestViews(APITestCase):

    def test_user_registration_with_valid_email(self):
        user_data = {'email': 'blackview5330pro@gmail.com', 'password': 'blackview5330pro@gmail.com',
                     'first_name': 'Oleg', 'last_name': 'Olegov', 'phone_number': '38093378344730',
                     'creation_time': datetime.now()}
        ulr = reverse('register_new_user')
        response = self.client.post(ulr, user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

