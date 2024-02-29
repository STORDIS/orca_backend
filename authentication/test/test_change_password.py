from django.contrib.auth.models import User

from authentication.test.test_authentication import TestAuthentication


class TestChangePasswordUser(TestAuthentication):

    def test_change_password_user(self):
        """
        Testing register user.
        """
        create_resp = self.client.post(
            path="/auth/user/register", format="json", data={
                "username": "test_user",
                "email": "test_user@gmail.com",
                "first_name": "first_name",
                "last_name": "last_name",
                "password": "test@123"
            },
            HTTP_AUTHORIZATION=self.tkn
        )
        assert create_resp.status_code == 200
        get_resp_1 = self.client.get(
            "/auth/user/test_user"
        )
        assert get_resp_1.status_code == 200
        user = User.objects.get(username='test_user')
        assert user.check_password("test@123")
        update_resp = self.client.put(
            path="/auth/user/change_password", format="json", data={
                "email": "test_user@gmail.com",
                "old_password": "test@123",
                "new_password": "test@1234"
            },
        )
        print(update_resp.json())
        user = User.objects.get(username='test_user')
        assert not user.check_password("test@123")
        assert user.check_password("test@1234")
        assert update_resp.status_code == 200
