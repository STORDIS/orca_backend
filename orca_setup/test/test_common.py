import yaml
from django.urls import reverse
from rest_framework.authtoken.admin import User
from rest_framework.test import APITestCase
from django.test import override_settings


# adding override_settings for celery to be eager it uses memory to store test tasks.
# eager is used because celery is not storing test tasks.
@override_settings(
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES_EXCEPTIONS=True,
    CELERY_TASK_STORE_EAGER_RESULT=True
)
class TestCommon(APITestCase):
    databases = ["default"]
    sonic_ips = []
    onie_ips = []
    sonic_img_details = {}

    def setUp(self):
        # Authenticate the user
        user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.force_authenticate(user)
        self.load_test_config()

        for device_ip in self.sonic_ips:
            response = self.get_req("device", {"mgt_ip": device_ip})
            if not response.data:
                response = self.put_req("discover", {"discover_from_config": True})
                if not response or response.get("result") == "Fail":
                    self.fail("Failed to discover devices")

    def load_test_config(self):
        file = "./network/test/test_orca_setup_config.yaml"
        with open(file, "r") as stream:
            try:
                config = yaml.safe_load(stream)
                self.sonic_ips = config["sonic_device_ips"]
                self.onie_ips = config["onie_device_ips"]
                self.sonic_img_details = config["sonic_img_details"]
            except yaml.YAMLError as exc:
                print(exc)

    def get_req(self, url_name: str, req_json=None):
        """
        Sends a GET request to the specified URL using the Django test client.

        Args:
            url_name (str): The name of the URL to be reversed and used in the request.
            req_json (Optional[Dict[str, Any]]): The JSON payload to be included in the request body. Defaults to None.

        Returns:
            Response: The response object returned by the GET request.

        Raises:
            AssertionError: If the URL name cannot be reversed.
        """
        print(f"Sending GET request to URL {url_name}, with payload: {req_json}")
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
