from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status


class ORCATest(APITestCase):
    device_ips = []
    ether_names = []

    def setUp(self):
        response = self.get_req("device_list")
        if not response.json():
            response = self.get_req("discover")
            if not response or response.get("result") == "Fail":
                self.fail("Failed to discover devices")

        for device in response.json():
            self.device_ips.append(device["mgt_ip"])

        if self.device_ips:
            response = self.get_req(
                "device_interface_list", {"mgt_ip": self.device_ips[0]}
            )
            while len(self.ether_names) < 5:
                if (
                    (intfs := response.json())
                    and (ifc := intfs.pop())
                    and ifc["name"].startswith("Ethernet")
                ):
                    self.ether_names.append(ifc["name"])

    def perform_del_port_chnl(self, request_body):
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
                self.assertFalse(response.json()["members"])
            else:
                self.assertIsNone(response.json())

            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def perform_add_port_chnl(self, request_body):
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
                {"mgt_ip": device_ip, "chnl_name": data.get("chnl_name")},
            )

            self.assertIsNone(response.json())
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            response = self.put_req("device_port_chnl", data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            response = self.get_req(
                "device_port_chnl",
                {"mgt_ip": device_ip, "chnl_name": data.get("chnl_name")},
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertTrue(
                response.json()["mtu"] == data["mtu"] if data.get("mtu") else True
            )
            self.assertTrue(
                response.json()["admin_sts"] == data.get("admin_status")
                if data.get("admin_status")
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
        self.perform_del_port_chnl(request_body)
        self.perform_add_port_chnl(request_body)
        self.perform_del_port_chnl(request_body)

    def get_req(self, url_name: str, req_json=None):
        return self.client.get(
            reverse(url_name),
            req_json,
            format="json",
        )

    def del_req(self, url_name: str, req_json):
        return self.client.delete(
            reverse(url_name),
            req_json,
            format="json",
        )

    def put_req(self, url_name: str, req_json):
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
