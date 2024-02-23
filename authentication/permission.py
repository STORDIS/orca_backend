import re

from django.contrib.auth.models import User
from oauth2_provider.oauth2_validators import AccessToken
from rest_framework import status
from rest_framework.permissions import BasePermission
from rest_framework.response import Response


class IsAdmin(BasePermission):

    """
    Gets is_staff attribute of token owner.
    """

    def has_permission(self, request, view) -> bool:
        """
        queries user details based on access_token.

        Returns:
            is_staff of user details `bool`
        """
        authorization = request.META["HTTP_AUTHORIZATION"]
        m = re.search(r'(Bearer)(\s)(.*)', authorization)
        token = m.group(3)
        token_user = AccessToken.objects.get(token=token)
        user = User.objects.get(username=token_user.user)
        return user.is_staff
