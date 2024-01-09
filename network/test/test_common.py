"""
Test utility functions
"""
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse


class ORCATest(APITestCase):
    """
    Test utility functions
    """

    device_ips = []
    ether_names = []

    def setUp(self):
        response = self.get_req("device")
        if not response.data:
            response = self.put_req("discover", {"discover_from_config":True})
            if not response or response.get("result") == "Fail":
                self.fail("Failed to discover devices")
        
        response = self.get_req("device")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        for device in response.json():
            self.device_ips.append(device["mgt_ip"])

        if self.device_ips:
            response = self.get_req(
                "device_interface_list", {"mgt_ip": self.device_ips[0]}
            )
            intfs = response.data
            if not intfs or not isinstance(intfs, list):
                return
            while len(self.ether_names) < 5:
                if (
                    (ifc := intfs.pop())
                    and ifc["name"].startswith("Ethernet")
                ):
                    self.ether_names.append(ifc["name"])

    def perform_del_port_chnl(self, request_body):
        """
        Perform the deletion of a port channel.

        Args:
            request_body (dict or list): The request body containing the information of the port channel to be deleted.

        Returns:
            None

        Raises:
            AssertionError: If the response status code is not 200 OK or if the response contains the message "resource not found".
                            If the response status code is not 204 NO CONTENT.
        """
        response = self.del_req("device_port_chnl", request_body)
        self.assertTrue(
            response.status_code == status.HTTP_200_OK
            or any(
                "resource not found" in res.lower() for res in response.json()["result"]
            )
        )
        for data in (
            request_body
            if isinstance(request_body, list)
            else [request_body]
            if request_body
            else []
        ):
            response = self.get_req("device_port_chnl", data)
            if data.get("members"):
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertFalse(response.json()["members"])
            else:
                self.assertTrue(response.status_code == status.HTTP_204_NO_CONTENT)
                self.assertFalse(response.data)

    def perform_add_port_chnl(self, request_body):
        """
        Perform the add port channel operation.

        Args:
            request_body (list or dict): The request body containing the data for the operation.

        Returns:
            None

        Raises:
            AssertionError: If the response status code is not 204 NO CONTENT or the response data is not empty.

        """
        for data in (
            request_body
            if isinstance(request_body, list)
            else [request_body]
            if request_body
            else []
        ):
            device_ip = data.get("mgt_ip")

            response = self.get_req(
                "device_port_chnl",
                {"mgt_ip": device_ip, "lag_name": data.get("lag_name")},
            )
            self.assertTrue(response.status_code == status.HTTP_204_NO_CONTENT)
            self.assertFalse(response.data)

            response = self.put_req("device_port_chnl", data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            response = self.get_req(
                "device_port_chnl",
                {"mgt_ip": device_ip, "lag_name": data.get("lag_name")},
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertTrue(
                response.json()["mtu"] == data["mtu"] if data.get("mtu") else True
            )
            self.assertTrue(
                response.json()["admin_sts"] == data.get("admin_sts")
                if data.get("admin_sts")
                else True
            )

            if data.get("members"):
                self.assertTrue(
                    all(
                        True if m in response.json()["members"] else False
                        for m in data.get("members")
                    )
                    and len(response.json()["members"]) == len(data.get("members"))
                )

    def perform_del_add_del_port_chnl(self, request_body):
        """
        Perform the following steps:
        1. Call the `perform_del_port_chnl` method with the `request_body` parameter.
        2. Call the `perform_add_port_chnl` method with the `request_body` parameter.
        3. Call the `perform_del_port_chnl` method with the `request_body` parameter.
        """
        self.perform_del_port_chnl(request_body)
        self.perform_add_port_chnl(request_body)
        self.perform_del_port_chnl(request_body)

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
        return self.client.put(
            reverse(url_name),
            req_json,
            format="json",
        )

    def get_speed_to_set(self, speed):
        """
        Get the speed to set based on the given speed.

        Args:
            speed (str): The current speed.

        Returns:
            str: The speed to set.

        Raises:
            None
        """
        if speed == "SPEED_40GB":
            speed_to_set = "SPEED_100GB"
        elif speed == "SPEED_100GB":
            speed_to_set = "SPEED_40GB"
        elif speed == "SPEED_10GB":
            speed_to_set = "SPEED_25GB"
        elif speed == "SPEED_25GB":
            speed_to_set = "SPEED_10GB"
        else:
            speed_to_set = "SPEED_25GB"
        return speed_to_set
