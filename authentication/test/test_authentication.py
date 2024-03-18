import json

from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase


class TestAuthentication(APITestCase):
    """Test Authentication apis"""
    user = None
    tkn = ""

    @classmethod
    def setUpClass(cls):
        # creating admin user for testing
        cls.user = User.objects.create(
            **{
                "username": "test_admin",
                "email": "test_admin@gmail.com",
                "first_name": "first_name",
                "last_name": "last_name",
                "password": make_password("test@123"),
                "is_staff": True
            }
        )
        cls.cls_atomics = cls._enter_atomics()
        return cls

    def setUp(self):
        resp = self.client.post(
            "/auth/login", {
                "username": "test_admin",
                "password": "test@123"
            }
        )
        assert resp.status_code == 200
        self.tkn = f"Token {resp.json()['token']}"
        self.client.credentials(HTTP_AUTHORIZATION=self.tkn)
        return self

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        return cls
