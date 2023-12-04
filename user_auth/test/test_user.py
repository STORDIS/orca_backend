## Generate test cases for user auth django application


## Generate test cases for user auth django application
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from user_auth.models import AppUser



class UserTestCase(APITestCase):
    # def setUp(self):
    #     self.client = Client()
    #     self.user = AppUser.objects.create_user(username='XXXXXXXX', password='XXXXXXXX')

    def test_login(self):
        response = self.client.post(
            reverse("login"), {"username": "test_user", "password": "password"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("home"))

    def test_logout(self):
        self.client.login(username="XXXXXXXX", password="XXXXXXXX")
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("login"))

    def test_register(self):
        req_body={'password': 'newpass1234562', 'last_login': None, 'email': 'test_email@email.com', 'username': 'test_user'}
        
        user = AppUser.objects.create_user('username', 'Pas$w0rd')
        response = self.client.post(
            reverse("register"),
            req_body,format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        ##test login after register
        # response = self.client.post(
        #     reverse("login"), req_body,format="json"
        # )
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
