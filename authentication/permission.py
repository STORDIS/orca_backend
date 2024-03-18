import re

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import NotFound
from rest_framework.permissions import BasePermission


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
        if (authorization := request.META.get("HTTP_AUTHORIZATION")) is None:
            raise NotFound("Authentication token not found")
        m = re.search(r'(Token)(\s)(.*)', authorization)
        token = m.group(3)
        token_user = Token.objects.get(key=token)
        user = User.objects.get(username=token_user.user)
        return user.is_staff
