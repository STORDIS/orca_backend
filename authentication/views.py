from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework import status, permissions, generics
from rest_framework.authtoken.models import Token
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from .permission import IsAdmin
from .serializers import RegisterSerializer


class UserList(generics.ListAPIView):
    """
    Class to get users list.
    """
    permission_classes = [IsAdmin]
    queryset = User.objects.all()
    serializer_class = RegisterSerializer


class RegisterView(APIView):

    """
    This Class adds users to database
    """

    permission_classes = [IsAdmin]

    def post(self, request):
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
            serializer = RegisterSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "successfully created."}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(data={"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoginView(APIView):

    """
    This Used to login user based on username name and password
    """

    def post(self, request):
        """
        A function to validate user and generate token.

        Parameters:
        - request: The Django request object.

        Returns:
        - If successful, returns a JSON response with token details and 200 ok status.
        - If user error, returns a JSON response with token details and 401 unauthorized status.
        - If fails returns a JSON response with 500 status.

        Required Keys:
        - username, password
        """
        try:
            data = request.data
            user = User.objects.get(username=data["username"])
            if not user.check_password(raw_password=data["password"]):
                return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(data={"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetUserView(APIView):
    """
    Class to get user based on username.
    """

    def get(self, request, **kwargs):
        """
        A function to get user.

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
            return Response(data=data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(data={"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeleteUserView(APIView):
    """
    A Class delete user from db.

    """
    permission_classes = [IsAdmin]

    def delete(self, request, **kwargs):
        """
        A function to delete user.

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
            if user:
                user.delete()
                return Response(data={"message": "Successfully deleted user."}, status=status.HTTP_200_OK)
            else:
                return Response(data={"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(data={"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChangePasswordView(APIView):
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
            return Response(data={"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateUserView(APIView):
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
            update_data = {k: v for k, v in data.items() if k not in ["is_staff", "is_superuser", "password"]}
            User.objects.filter(email=email).update(**update_data)
            return Response(data={"message": "Update successful."}, status=status.HTTP_200_OK)
        except KeyError as e:
            return Response(data={"message": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(data={"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateIsStaffView(APIView):
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
            update_data = {"is_staff": True if kwargs.get("value") == "true" else False}
            User.objects.filter(email=email).update(**update_data)
            return Response(data={"message": "Update successful."}, status=status.HTTP_200_OK)
        except KeyError as e:
            return Response(data={"message": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(data={"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
