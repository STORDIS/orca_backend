from authentication.test.test_authentication import TestAuthentication


class TestAddAdminUser(TestAuthentication):

    def test_add_admin_user(self):
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
        update_resp_1 = self.client.put(
            path="/auth/user/is_admin/true", format="json", data={
                "email": "test_user@gmail.com",
            },
        )
        assert update_resp_1.status_code == 200
        print(update_resp_1.json())
        get_resp_2 = self.client.get(
            "/auth/user/test_user"
        )
        assert get_resp_2.status_code == 200
        assert get_resp_2.json()["is_staff"]
        update_resp_2 = self.client.put(
            path="/auth/user/is_admin/false", format="json", data={
                "email": "test_user@gmail.com",
            },
        )
        assert update_resp_2.status_code == 200
        get_resp_3 = self.client.get(
            "/auth/user/test_user"
        )
        assert get_resp_3.status_code == 200
        assert not get_resp_3.json()["is_staff"]
