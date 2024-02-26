import datetime
import json

from django.contrib.auth.models import User
from oauth2_provider.models import Application
from oauth2_provider.oauth2_validators import AccessToken
from rest_framework.permissions import AllowAny
from rest_framework.test import APITestCase


class TestAuthentication(APITestCase):
    permission_classes = (AllowAny,)
    """Test Authentication apis"""
    tkn = ""

    def setUp(self):
        User.objects.create(
            **{
                "username": "test_admin",
                "email": "test_admin@gmail.com",
                "first_name": "first_name",
                "last_name": "last_name",
                "password": "test@123",
                "is_staff": True
            }
        )
        user = User.objects.get(username='test_admin')
        client = Application(
            client_id='orca_id',
            client_secret='orca_secret',
            client_type='confidential',
            authorization_grant_type='password',
        )
        client.save()
        application = Application.objects.get(client_id='orca_id')
        access_token = AccessToken.objects.create(
            user=user,
            application=application,
            token='your_access_token',
            expires=datetime.datetime.now() + datetime.timedelta(days=1),
            scope='read write',
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        return self