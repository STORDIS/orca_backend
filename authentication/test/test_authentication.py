import json

from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase


class TestAuthentication(APITestCase):
    """Test Authentication apis"""
    tkn = ""

    def setUp(self):
        User.objects.create(
            **{
                "username": "test_admin",
                "email": "test_admin@gmail.com",
                "first_name": "first_name",
                "last_name": "last_name",
                "password": make_password("test@123"),
                "is_staff": True
            }
        )
        resp = self.client.post(
            "/auth/login", {
                "username": "test_admin",
                "password": "test@123"
            }
        )
        self.tkn = f"Token {resp.json()['token']}"
        self.client.credentials(HTTP_AUTHORIZATION=self.tkn)
        return self
