"""
This module contains tests for the Interface API.
"""

from rest_framework import status
from django.urls import reverse

from network.test.test_common import ORCATests


class PortChnlAPITestCase(ORCATests):
    """
    This class contains tests for the Interface API.
    """

    def test_put_device_Portchannel(self):
        device_ip = self.retrieve_device()[0]
        chnl_name = "PortChannel101"
        response = self.client.get(
            reverse("device_port_chnl"),
            {"mgt_ip": device_ip, "chnl_name": chnl_name},
        )
        if response.json() and (chnl_name := response.json()["lag_name"]):
            self.client.delete(
                reverse("device_port_chnl"),
                {"mgt_ip": device_ip, "chnl_name": chnl_name},
            )

        response = self.client.get(
            reverse("device_port_chnl"),
            {"mgt_ip": device_ip, "chnl_name": chnl_name},
        )
        self.assertIsNone(response.json())

        # mtu
        request_body = [
            {
                "mgt_ip": device_ip,
                "chnl_name": chnl_name,
                "mtu": 8000,
                "admin_status": "up",
            }
        ]
        for data in request_body:
            response = self.client.put(reverse("device_port_chnl"), data)
            response = self.client.get(
                reverse("device_port_chnl"),
                {"mgt_ip": device_ip, "chnl_name": chnl_name},
            )
        self.assertEqual(response.json()["mtu"], data["mtu"])
        self.assertEqual(response.json()["admin_sts"], data["admin_status"])

        if response.json() and (chnl_name := response.json()["lag_name"]):
            self.client.delete(
                reverse("device_port_chnl"),
                {"mgt_ip": device_ip, "chnl_name": chnl_name},
            )

        response = self.client.get(
            reverse("device_port_chnl"),
            {"mgt_ip": device_ip, "chnl_name": chnl_name},
        )
        self.assertIsNone(response.json())

    #    Multiple Portchannels update request

    def test_multiple_portchanls_list(self):
        device_ip = self.retrieve_device()[0]
        request_body = [
            {
                "mgt_ip": device_ip,
                "chnl_name": "PortChannel103",
                "mtu": "9100",
                "admin_status": "down",
            },
            {
                "mgt_ip": device_ip,
                "chnl_name": "PortChannel102",
                "mtu": "9200",
                "admin_status": "down",
            },
        ]

        for req in request_body:
            chnl_name = req["chnl_name"]
            response = self.client.get(
                reverse("device_port_chnl"),
                {"mgt_ip": device_ip, "chnl_name": chnl_name},
            )
            if response.json() and chnl_name == response.json()["lag_name"]:
                self.client.delete(
                    reverse("device_port_chnl"),
                    {"mgt_ip": device_ip, "chnl_name": chnl_name},
                )

            response = self.client.get(
                reverse("device_port_chnl"),
                {"mgt_ip": device_ip, "chnl_name": chnl_name},
            )
            self.assertIsNone(response.json())

        response = self.client.put(
            reverse("device_port_chnl"), request_body, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"status": "Config Successful"})
        response = self.client.delete(
            reverse("device_port_chnl"), request_body, format="json"
        )

        for req in request_body:
            chnl_name = req["chnl_name"]
            response = self.client.get(
                reverse("device_port_chnl"),
                {"mgt_ip": device_ip, "chnl_name": chnl_name},
            )
            self.assertIsNone(response.json())
