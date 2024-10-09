from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIRequestFactory, APITransactionTestCase
from log_manager.models import Logs


class TestCommon(APITransactionTestCase):
    user = None
    tkn = ""
    factory = APIRequestFactory()

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
        return cls

    def setUp(self):
        user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.force_authenticate(user)
        return self

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        Logs.objects.all().delete()
        return cls
