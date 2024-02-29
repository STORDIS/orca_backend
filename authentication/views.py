import json
import traceback

import requests
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpRequest
from oauth2_provider.oauth2_validators import RefreshToken, AccessToken
from oauth2_provider.views import TokenView
from oauthlib.oauth2 import InvalidGrantError
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response

from authentication.models import CreateUserForm
from authentication.permission import IsAdmin
from authentication.serializers import UserSerializer


class UserList(generics.ListCreateAPIView):
    permission_classes = [IsAdmin]
    queryset = User.objects.all()
    serializer_class = UserSerializer


@api_view(['get'])
def callback(request: HttpRequest | Request):
    # resp = requests.get("auth/o/token", )
    try:
        query_params = request.query_params
        url = 'http://localhost:8000/auth/o/token/'
        body = {
            "code": query_params.get("code"),
            "grant_type": "authorization_code",
            "redirect_uri": "http://localhost:8000/auth/callback",
            "client_id": "orca_id",
        }
        resp = requests.post(url=url, data=json.dumps(body), headers={
            "Content-Type": "application/x-www-form-urlencoded"
        })
        print(url)
        print(json.dumps(body, indent=4))
        return Response(resp.text, status=status.HTTP_200_OK)
    except Exception as e:
        print(str(e))
        return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CustomTokenView(TokenView):
    def post(self, request, *args, **kwargs):
        print(request.body)
        try:
            return super().post(request, *args, **kwargs)
        except InvalidGrantError as e:
            return JsonResponse({'error': 'invalid_grant', 'error_description': str(e)})


@api_view(['post'])
def login(request: Request):
    # resp = requests.get("auth/o/token", )
    """
    Login function creates auth tokens.

    Parameters:
    - request: The Django request object.

    Returns:
    - If successful, returns a JSON response with token details and 200 ok status.
    - If fails returns a JSON response with 500 status.
    """
    try:
        data = request.data
        url = 'http://localhost:8000/auth/o/token/'
        body = {
            "grant_type": "password",
            "client_id": "orca_id",
            **data
        }
        resp = requests.post(
            url=url, data=json.dumps(body)
        )
        if resp.status_code == 200:
            return Response(resp.json(), status=status.HTTP_200_OK)
        else:
            return Response(resp.json(), status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        print(str(e))
        return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['post'])
def generate_refresh_token(request: Request):
    # resp = requests.get("auth/o/token", )
    """
    refreshes auth tokens.

    Parameters:
    - request: The Django request object.

    Returns:
    - If successful, returns a JSON response with token details and 200 ok status.
    - If fails returns a JSON response with 500 status.
    """
    try:
        data = request.data
        refresh_token = RefreshToken.objects.get(token=data["refresh_token"])
        url = 'http://localhost:8000/auth/o/token/'
        response = requests.post(
            url=url,
            data=json.dumps({
                "refresh_token": refresh_token.token,
                "grant_type": "refresh_token",
                "client_id": refresh_token.access_token.application.client_id
            })
        )
        return Response(response.json(), status=status.HTTP_200_OK)
    except Exception as e:
        print(str(e))
        return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CreateUserView(generics.CreateAPIView):
    """
    Class to add user to db
    """
    permission_classes = [IsAdmin]  # checks is_staff value

    def post(self, request: Request, **kwargs):
        """
        A function to add user.

        Parameters:
        - request: The Django request object.

        Returns:
        - If successful, returns a JSON response with token details and 200 ok status.
        - If user error, returns a JSON response with token details and 400 bad request status.
        - If fails returns a JSON response with 500 status.

        Required Keys:
        - email, username, password, first_name, last_name.
        """
        try:
            # user = User.objects.create_user(username=kwargs.get("pk"), **request.data)
            # user.save()
            data = request.data
            password = make_password(data.pop("password"))
            user = CreateUserForm(data={**data, "password": password})
            if user.is_valid():
                user.save()
                return Response(
                    data={"message": "successfully created."},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    data={"message": user.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            print(e)
            return Response(
                data={"message": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class GetUserView(generics.RetrieveAPIView):
    """
    Class to get user based on username.
    """

    def get(self, request, **kwargs):
        """
        A function to add user.

        Parameters:
        - request: The Django request object.

        Returns:
        - If successful, returns a JSON response with token details and 200 ok status.
        - If fails returns a JSON response with 500 status.

        Required Keys:
        - username.
        """
        try:
            user = User.objects.get(username=kwargs.get("pk"))
            data = {
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_staff": user.is_staff
            }
            return Response(
                data=data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            print(e)
            return Response(
                data={"message": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class DeleteUserView(generics.DestroyAPIView):
    """
    A Class delete password.

    Checks user authenticated based on token.
    """

    permission_classes = [IsAdmin]

    def delete(self, request, *args, **kwargs):
        """
        A function to change password.

        Parameters:
        - request: The Django request object.

        Returns:
        - If successful, returns a JSON response with token details and 200 ok status.
        - If key error, returns a JSON response with token details and 404 status.
        - If fails returns a JSON response with 500 status.

        Required Keys:
        - email.
        """
        try:
            data = request.data
            user = get_object_or_404(User.objects.filter(email=data["email"]))
            user.delete()
            return Response(data={"message": "Successfully updated user data."}, status=status.HTTP_200_OK)
        except KeyError as e:
            return Response(data={"message": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            return Response(data={"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChangePasswordView(generics.UpdateAPIView):
    """
    A Class update password.

    Checks user authenticated based on token.
    """

    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, **kwargs):
        """
        A function to change password.

        Parameters:
        - request: The Django request object.

        Returns:
        - If successful, returns a JSON response with token details and 200 ok status.
        - If key error, returns a JSON response with token details and 404 status.
        - If fails returns a JSON response with 500 status.

        Required Keys:
        - old_password, new_password, email.
        """
        try:
            data = request.data
            user = get_object_or_404(User.objects.filter(email=data["email"]))
            if user.check_password(data["old_password"]):
                user.set_password(data["new_password"])
                user.save()
                return Response(data={"message": "Successfully saved password."}, status=status.HTTP_200_OK)
            else:
                return Response(data={"message": "Old password is not correct."}, status=status.HTTP_404_NOT_FOUND)
        except KeyError as e:
            return Response(data={"message": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            return Response(data={"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateUserView(generics.UpdateAPIView):
    """
    A Class update user data.

    Checks user authenticated based on token.
    """

    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, **kwargs):
        """
        A function to change password.

        Parameters:
        - request: The Django request object.

        Returns:
        - If successful, returns a JSON response with token details and 200 ok status.
        - If key error, returns a JSON response with token details and 404 status.
        - If fails returns a JSON response with 500 status.

        Required Keys:
        - email.
        """
        try:
            data = request.data
            email = data.pop("email", "")
            # user = get_object_or_404(User.objects.filter(email=email))
            update_data = {k: v for k, v in data.items() if k not in ["is_staff", "is_superuser", "password"]}
            User.objects.filter(email=email).update(**update_data)
            return Response(data={"message": "Update successful."}, status=status.HTTP_200_OK)
        except KeyError as e:
            print(e)
            return Response(data={"message": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            return Response(data={"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateIsStaffView(generics.UpdateAPIView):
    """
    A Class update user data.

    Checks user authenticated based on token.
    """

    permission_classes = [IsAdmin]

    def put(self, request, **kwargs):
        """
        A function to change is_staff.

        Parameters:
        - request: The Django request object.

        Returns:
        - If successful, returns a JSON response with token details and 200 ok status.
        - If key error, returns a JSON response with token details and 404 status.
        - If fails returns a JSON response with 500 status.

        Required Keys:
        - email.
        """
        try:
            data = request.data
            email = data.pop("email", "")
            # user = get_object_or_404(User.objects.filter(email=email))
            update_data = {"is_staff": True if kwargs.get("value") == "true" else False}
            User.objects.filter(email=email).update(**update_data)
            return Response(data={"message": "Update successful."}, status=status.HTTP_200_OK)
        except KeyError as e:
            print(e)
            return Response(data={"message": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            return Response(data={"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
