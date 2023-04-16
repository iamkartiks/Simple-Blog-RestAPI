from django.test import TestCase
from django.contrib import auth
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

class AuthTestCase(TestCase):
    def setUp(self):
        self.u = auth.User.objects.create_user('test@dom.com', 'test@dom.com', 'pass')
        self.u.is_staff = True
        self.u.is_superuser = True
        self.u.is_active = True
        self.u.save()

    def testLogin(self):
        self.client.login(username='test@dom.com', password='pass')

class UsersAPIViewTestCase(APITestCase):
    def setUp(self):
        self.url = reverse('users')
        self.valid_payload = {'username': 'testuser', 'email': 'testuser@example.com'}
        self.invalid_payload = {'username': 'invaliduser'}

    def test_get_all_users(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_valid_user(self):
        response = self.client.post(self.url, data=self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invalid_user(self):
        response = self.client.post(self.url, data=self.invalid_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)