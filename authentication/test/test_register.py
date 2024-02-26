from authentication.test.test_authentication import TestAuthentication


class TestRegister(TestAuthentication):

    def test_register_user(self):
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
        get_resp = self.client.get(
            "/auth/user/test_user"
        )
        assert get_resp.status_code == 200

    def test_failure(self):
        """
        Testing Missing user attributes.
        """
        create_resp = self.client.post(
            path="/auth/user/register", format="json", data={
                "first_name": "first_name",
                "last_name": "last_name",
                "password": "test@123"
            },
            HTTP_AUTHORIZATION=self.tkn
        )
        assert create_resp.status_code == 400

