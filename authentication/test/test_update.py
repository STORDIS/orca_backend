from authentication.test.test_authentication import TestAuthentication


class TestUpdateUser(TestAuthentication):

    def test_update_user(self):
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
        update_resp = self.client.put(
            path="/auth/user/update", format="json", data={
                "email": "test_user@gmail.com",
                "first_name": "value"
            },
        )
        print(update_resp.json())
        assert update_resp.status_code == 200
        get_resp_2 = self.client.get(
            "/auth/user/test_user"
        )
        print(get_resp_2.json())
        assert get_resp_2.status_code == 200
        assert get_resp_2.json()["first_name"] == "value"
