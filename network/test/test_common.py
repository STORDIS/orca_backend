"""
Test utility functions
"""

import time
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from orca_nw_lib.gnmi_sub import gnmi_unsubscribe_for_all_devices_in_db
from django.contrib.auth.models import User


class TestORCA(APITestCase):
    """
    Test utility functions
    """

    device_ips = []
    ether_names = []

    sync_done = False

    def setUp(self):
        ## Autheticate the user
        user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.force_authenticate(user)

        response = self.get_req("device")
        ## If not devices discovered yet, discover them first.
        if not response.data:
            response = self.put_req("discover", {"discover_from_config": True})
            if not response or response.get("result") == "Fail":
                self.fail("Failed to discover devices")

        response = self.get_req("device")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for device in response.json():
            self.device_ips.append(device["mgt_ip"])
            break  ## only one device is enough for tests

        if self.device_ips:
            response = self.get_req(
                "device_interface_list", {"mgt_ip": self.device_ips[0]}
            )
            intfs = response.data
            if not intfs or not isinstance(intfs, list):
                return
            while len(self.ether_names) < 4:
                if (ifc := intfs.pop()) and ifc["name"].startswith("Ethernet"):
                    self.ether_names.append(ifc["name"])

        if not TestORCA.sync_done:
            # Resync the interfaces, because may be their state has been modified when ORCA was not up,
            # or state wasn't updated in DB due to cancelling the test case prematurely because of debugging.
            # Which may cause the test case to fail. For example while changing the enable state of an interface,
            # Test case might read DB first, to see the current value of enable state and apply opposite value.
            # But if the enable state wasn't correct in DB it might lead to setting the same enable state again.
            # In this case subscription response will not be generated .
            # Hence resulting in test failure.
            for ip in self.device_ips:
                for if_name in self.ether_names:
                    response1 = self.post_req(
                        "interface_resync", {"mgt_ip": ip, "name": if_name}
                    )
                    self.assertEqual(response1.status_code, status.HTTP_200_OK)
                TestORCA.sync_done = True

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        gnmi_unsubscribe_for_all_devices_in_db()

    def del_port_chnl_ip(self, request_body):
        for data in (
            request_body
            if isinstance(request_body, list)
            else [request_body] if request_body else []
        ):
            if "lag_name" in data and "mgt_ip" in data:
                device_ip = data["mgt_ip"]
                port_channel = data["lag_name"]
                ip_address = data.get("ip_address", None)

                del_resp = self.del_req(
                    "port_channel_ip_remove",
                    {
                        "mgt_ip": device_ip,
                        "lag_name": port_channel,
                        "ip_address": ip_address,
                    },
                )
                ## 200_OK incase of IP has been successfully removed, and "resource not found" incase of IP was not there before removal
                self.assert_response_status(
                    del_resp, status.HTTP_200_OK, "resource not found"
                )
                response = self.get_req(
                    "device_port_chnl", {"mgt_ip": device_ip, "lag_name": port_channel}
                )
                self.assertTrue(
                    response.status_code
                    == status.HTTP_204_NO_CONTENT  ## PortChannel does not exist
                    or response.json()["ip_address"]
                    == None  ## Portchannel exists but ip_address is None
                )

    def assert_response_status(
        self, response, expected_status_codes, expected_response_msg=None
    ):
        try:
            self.assertTrue(
                (
                    response.status_code in expected_status_codes
                    if isinstance(expected_status_codes, list)
                    else [expected_status_codes] if expected_status_codes else []
                ),
                f"Expected status code to be one of {expected_status_codes}, but got {response.status_code}",
            )
        except AssertionError as e:
            print("Assertion Error : ", e)
            print(f"Response Code : {response.status_code}")
            # Check for the expected string in the 'result' field if provided
            if expected_response_msg is not None:
                result = response.json().get("result", [])
                try:
                    self.assertTrue(
                        any(
                            expected_response_msg in res.get("message", "").lower()
                            for res in result
                            if res != "\n"
                        ),
                        f"Expected string '{expected_response_msg}' not found in response 'result' field: {result}",
                    )
                except AssertionError as e:
                    print("Assertion Error : ", e)
                    print(f"Response: {response.json()}")
                    raise

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
        self.remove_all_mem_vlan_of_port_chnl(request_body)
        # remove ip_address from port channel first otherwise port channel deletion will fail
        self.del_port_chnl_ip(request_body)
        # delete port channel member ethernet
        self.assert_response_status(
            self.del_req("port_chnl_mem_ethernet", request_body),
            status.HTTP_200_OK,
            "resource not found",
        )
        # delete port channel member vlan
        self.assert_response_status(
            self.del_req("device_port_chnl", request_body),
            [status.HTTP_200_OK],
            "resource not found",
        )
        for data in (
            request_body
            if isinstance(request_body, list)
            else [request_body] if request_body else []
        ):
            response = self.get_req("device_port_chnl", data)
            self.assert_response_status(response, status.HTTP_204_NO_CONTENT)
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
            self.assert_response_status(
                self.put_req("device_port_chnl", data), status.HTTP_200_OK
            )
            response = self.get_req("device_port_chnl", data)
            self.assert_response_status(response, status.HTTP_200_OK)
            self.assertTrue(
                response.json().get("mtu") == data.get("mtu") if data.get("mtu") else True
            )
            self.assertTrue(
                response.json()["admin_sts"] == data.get("admin_status")
                if data.get("admin_status")
                else True
            )

    def perform_add_port_chnl_mem_eth(self, request_body):

        for data in (
            request_body
            if isinstance(request_body, list)
            else [request_body] if request_body else []
        ):
            self.assert_response_status(
                self.put_req("port_chnl_mem_ethernet", data), status.HTTP_200_OK
            )
            response = self.get_req("device_port_chnl", data)
            self.assert_response_status(response, status.HTTP_200_OK)
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

    def get_valid_speeds(self, speed):
        if speed == "SPEED_25GB":
            return "25000"
        elif speed == "SPEED_10GB":
            return "10000,1000"
        else:
            pass

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

    def send_req_and_assert(self, req_func, *req_args, **assert_args):
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
                    self.assertEqual(response.status_code, value)
                continue
            if response.status_code not in [
                status.HTTP_200_OK,
                status.HTTP_204_NO_CONTENT,
                status.HTTP_201_CREATED,
            ]:
                print(response.data)
            if response.status_code == status.HTTP_200_OK:
                print(f"Received {key} value: {response.json()[key]}")
                self.assertEqual(response.json()[key], value)
        return response

    def assert_with_timeout_retry(self, req_func, *req_args, **assert_args):
        """
        Executes a given function with a timeout and retries in case of failure.
        Usefull when executing a function that spawns a multiple a threads. Following can be the scenarios:
        Case-1 :
            While making update requests. Device might be subscribed but haven't received the sync_response:true message.
            before receiving this message it will be ready to receive any subscription responses for any config done via any put, post, delete, patch requests.
        Case-2 :
            While making get requests for the config verification done previously, there can be delay in receiving the subscription response from the device.

        Args:
            req_func (Callable): The function to make the request to orca.
            *req_args: The arguments to pass to req_func. t.e. req url and payload.
            **assert_args: The arguments to pass to assert_func. t.e. assert status code and response.
        """
        timeout = 2
        retries = 10
        for _ in range(retries):
            try:
                return self.send_req_and_assert(req_func, *req_args, **assert_args)
            except AssertionError:
                print(
                    f"Assertion failed for request args: {req_args}, and assert args: {assert_args}"
                )
                print(f"Retrying in {timeout} seconds")
                time.sleep(timeout)
                continue
        return self.send_req_and_assert(req_func, *req_args, **assert_args)

    def remove_mclag(self, device_ip):
        response = self.del_req("device_mclag_list", {"mgt_ip": device_ip})
        self.assertTrue(
            response.status_code == status.HTTP_200_OK
            or any(
                "resource not found" in res.get("message", "").lower()
                for res in response.json()["result"]
                if res != "\n"
            )
        )
        response = self.get_req("device_mclag_list", {"mgt_ip": device_ip})
        self.assertTrue(response.status_code == status.HTTP_204_NO_CONTENT)
        self.assertFalse(response.data)

    def remove_all_mem_vlan_of_port_chnl(self, request_body):
        # req = {"mgt_ip": device_ip, "lag_name": lag_name}
        ## Remove all member VLANs before deleting port channel Otherwise, it will give an erros that instance is in use.
        for data in (
            request_body
            if isinstance(request_body, list)
            else [request_body] if request_body else []
        ):
            if "lag_name" in data and "mgt_ip" in data:
                response = self.get_req("device_port_chnl", data)
                if response.status_code == status.HTTP_200_OK:
                    ## If Port channel exists, only then try to remove member vLANs from it
                    response = self.del_req(
                        "port_chnl_vlan_member_remove_all", req_json=data
                    )
                    self.assert_response_status(
                        response, status.HTTP_200_OK, "resource not found"
                    )

                    ## Now assert that Member vlan has been removed from Port channel
                    response = self.get_req("device_port_chnl", data)
                    self.assert_response_status(response, status.HTTP_200_OK)
                    self.assertFalse(
                        response.json().get("vlan_members"),
                        f"Was not expecting any vlan_members of port channel {data['lag_name']}, but got: {response.json().get('vlan_members')}",
                    )

    def create_vlan(self, req_payload):
        response = self.del_req(
            "vlan_ip_remove",
            {"mgt_ip": req_payload["mgt_ip"], "name": req_payload["name"]},
        )

        self.assertTrue(
            response.status_code == status.HTTP_200_OK
            or any(
                "not found" in res.get("message", "").lower()
                for res in response.json()["result"]
                if res != "\n"
            )
        )
        response = self.del_req(
            "vlan_config",
            {"mgt_ip": req_payload["mgt_ip"], "name": req_payload["name"]},
        )

        self.assertTrue(
            response.status_code == status.HTTP_200_OK
            or any(
                "not found" in res.get("message", "").lower()
                for res in response.json()["result"]
                if res != "\n"
            )
        )

        response = self.get_req(
            "vlan_config",
            {"mgt_ip": req_payload["mgt_ip"], "name": req_payload["name"]},
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(response.data)

        response = self.put_req(
            "vlan_config",
            req_payload,
        )
        ## Assert that vlan is created successfully
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.get_req(
            "vlan_config",
            {"mgt_ip": req_payload["mgt_ip"], "name": req_payload["name"]},
        )
        self.assertEqual(response.json()["name"], req_payload["name"])
        if req_vlanid := req_payload.get("vlanid"):
            self.assertEqual(response.json()["vlanid"], req_vlanid)
        if req_mtu := req_payload.get("mtu"):
            self.assertEqual(response.json()["mtu"], req_mtu)
        if req_enabled := req_payload.get("enabled"):
            self.assertEqual(response.json()["enabled"], req_enabled)
        if req_description := req_payload.get("description"):
            self.assertEqual(response.json()["description"], req_description)
        if req_autostate := req_payload.get("autostate"):
            self.assertEqual(response.json()["autostate"], req_autostate)
        if req_ip_address := req_payload.get("ip_address"):
            self.assertEqual(response.json()["ip_address"], req_ip_address)
        if sag_ips := req_payload.get("sag_ip_address"):
            self.assertEqual(response.json()["sag_ip_address"], sag_ips)

    def delete_vlan(self, req_payload):
        response = self.del_req(
            "vlan_config",
            {"mgt_ip": req_payload["mgt_ip"], "name": req_payload["name"]},
        )

        self.assertTrue(
            response.status_code == status.HTTP_200_OK
            or any(
                "resource not found" in res.get("message", "").lower()
                for res in response.json()["result"]
                if res != "\n"
            )
        )

        response = self.get_req(
            "vlan_config",
            {"mgt_ip": req_payload["mgt_ip"], "name": req_payload["name"]},
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
