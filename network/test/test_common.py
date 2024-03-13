"""
Test utility functions
"""

import time
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from orca_nw_lib.gnmi_sub import gnmi_unsubscribe_for_all_devices_in_db


class ORCATest(APITestCase):
    """
    Test utility functions
    """

    device_ips = []
    ether_names = []

    def setUp(self):
        response = self.get_req("device")
        if not response.data:
            response = self.put_req("discover", {"discover_from_config": True})
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
                if (ifc := intfs.pop()) and ifc["name"].startswith("Ethernet"):
                    self.ether_names.append(ifc["name"])
                    
        ## Resync the interfaces, may be their state has been modified when ORCA was not up,
        ## or state wasn't updated in DB due to cancelling the test case repmaturly because of debugging.
        for ip in self.device_ips:
            for if_name in self.ether_names:
                response1 = self.post_req(
                    "interface_resync", {"mgt_ip": ip, "name": if_name}
                )
                self.assertEqual(response1.status_code, status.HTTP_200_OK)

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        gnmi_unsubscribe_for_all_devices_in_db()

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
            else [request_body] if request_body else []
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
            else [request_body] if request_body else []
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
        
    def post_req(self, url_name: str, req_json):
        return self.client.post(
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

    def get_common_speed_to_set(self, speed):
        """
        Get the speed to set based on the given speed.

        Args:
            speed (str): The current speed.

        Returns:
            str: The speed to set.

        Raises:
            None
        """
        if speed in ["SPEED_40GB", "SPEED_100GB"]:
            speed_to_set = "SPEED_40GB"
        elif speed in ["SPEED_10GB", "SPEED_25GB"]:
            speed_to_set = "SPEED_10GB"
        else:
            speed_to_set = "SPEED_10GB"
        return speed_to_set

    def send_req_and_assert(self, req_func, assert_func, *req_args, **assert_args):
        response = req_func(*req_args)
        for key, value in assert_args.items():
            print(f"Asserting against key: {key}, value: {value}")
            if key == "status":
                print(f"Received {key} code: {response.status_code}")
                if isinstance(value, list):
                    ## Need to check multiple status codes
                    self.assertTrue(
                        response.status_code in value,
                    )
                else:
                    assert_func(response.status_code, value)
                continue
            if response.status_code == status.HTTP_200_OK:
                print(f"Received {key} value: {response.json()[key]}")
                assert_func(response.json()[key], value)
        return response

    def assert_with_timeout_retry(
        self, req_func, assert_func, *req_args, **assert_args
    ):
        """
        Executes a given function with a timeout and retries in case of failure.
        Usefull when executing a function that spawns a multiple athreads. Following can be the scenarios:
        Case-1 :
            While making update requests. Device might be subscribed but haven't received the sync_response:true message.
            before receiving this message it will be ready to receive any subscription responses for any config done via any put, post, delete, patch requests.
        Case-2 :
            While making get requests for the config verification done previously, there can be delay in receiving the subscription response from the device.

        Args:
            req_func (Callable): The function to make the request to orca.
            assert_func (Callable): The function to assert the response returned by req_func.
            *req_args: The arguments to pass to req_func. t.e. req url and payload.
            **assert_args: The arguments to pass to assert_func. t.e. assert status code and response.
        """
        timeout = 2
        retries = 10
        for _ in range(retries):
            try:
                return self.send_req_and_assert(
                    req_func, assert_func, *req_args, **assert_args
                )
            except AssertionError:
                print(f"Assertion failed for request args: {req_args}, and assert args: {assert_args}")
                print(f"Retrying in {timeout} seconds")
                time.sleep(timeout)
                continue
        return self.send_req_and_assert(req_func, assert_func, *req_args, **assert_args)
