from django.urls import reverse
from rest_framework.authtoken.admin import User
from rest_framework.test import APITransactionTestCase


class TestCommon(APITransactionTestCase):

    def setUp(self):
        # Authenticate the user
        user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.force_authenticate(user)

    def get_req(self, url_name: str, req_json=None, args=None):
        """
        Sends a GET request to the specified URL using the Django test client.

        Args:
            url_name (str): The name of the URL to be reversed and used in the request.
            req_json (Optional[Dict[str, Any]]): The JSON payload to be included in the request body. Defaults to None.
            args (Optional[List[Any]]): The arguments to be passed to the URL pattern. Defaults to None.
        Returns:
            Response: The response object returned by the GET request.

        Raises:
            AssertionError: If the URL name cannot be reversed.
        """
        print(f"Sending GET request to URL {url_name}, with payload: {req_json}")
        if args:
            return self.client.get(
                reverse(url_name, args=args),
                req_json,
                format="json",
            )
        return self.client.get(
            reverse(url_name),
            req_json,
            format="json",
        )

    def del_req(self, url_name: str, req_json=None):
        """
        Delete a resource using a DELETE request to the specified URL.

        Args:
            url_name (str): The name of the URL pattern to reverse and use as the endpoint.
            req_json: The JSON payload to be sent with the request.

        Returns:
            The response from the DELETE request.

        Raises:
            None.
        """
        print(f"Sending DEL request to URL {url_name}, with payload: {req_json}")
        return self.client.delete(
            reverse(url_name),
            req_json,
            format="json",
        )

    def put_req(self, url_name: str, req_json):
        """
        Sends a PUT request to the specified URL.

        Args:
            url_name (str): The name of the URL to request.
            req_json: The JSON data to send with the request.

        Returns:
            The response from the request in JSON format.
        """
        print(f"Sending PUT request to URL {url_name}, with payload: {req_json}")
        return self.client.put(
            reverse(url_name),
            req_json,
            format="json",
        )
