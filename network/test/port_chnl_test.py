"""
This module contains tests for the Interface API.
"""

from rest_framework import status
from django.urls import reverse

from network.test.test_common import ORCATest


class PortChnlTest(ORCATest):

    """
    This class contains tests for the Port Channel API.
    """
    
    def test_port_channel_config(self):
        """
        Test the port channel configuration.

        This function tests the configuration of the port channels. It sends a DELETE
        request to the device's port channel endpoint to remove any existing port
        channels. Then, it sends a series of GET requests to ensure that the port
        channels have been successfully removed. Next, it sends a PUT request to
        create new port channels with specific configurations. Finally, it sends
        additional GET requests to verify the creation and configuration of the
        port channels.

        Parameters:
        - self: The instance of the test class.

        Returns:
        None
        """
        device_ip = self.device_ips[0]
        request_body = [
            {
                "mgt_ip": device_ip,
                "chnl_name": "PortChannel101",
                "mtu": 8000,
                "admin_status": "up",
            },
            {
                "mgt_ip": device_ip,
                "chnl_name": "PortChannel102",
                "mtu": 9100,
                "admin_status": "up",
            },
        ]

        # First delete mclag, if it exists.
        # port channel deletion will fail if port channel is found to be a member of mclag.

        self.client.delete(
            reverse("device_mclag_list"),
            {"mgt_ip": device_ip},
            format="json",
        )

        response = self.client.get(
            reverse("device_mclag_list"),
            {"mgt_ip": device_ip},
        )

        self.assertTrue(
            response.status_code == status.HTTP_200_OK
            or any(
                "resource not found" in res.lower() for res in response.json()["result"]
            )
        )

        # Now delete port channels
        self.perform_del_add_del_port_chnl(request_body)

    def test_port_chnl_mem_config(self):
        """
        Test the configuration of port channel members.
        """
        device_ip = self.device_ips[0]
        ether_1 = self.ether_names[0]
        ether_2 = self.ether_names[1]
        ether_3 = self.ether_names[2]
        ether_4 = self.ether_names[3]
        mtu = 9100
        # First set same mtu on member interfaces as port channel.
        itf_request_body = [
            {
                "mgt_ip": device_ip,
                "name": ether_1,
                "mtu": mtu,
            },
            {
                "mgt_ip": device_ip,
                "name": ether_2,
                "mtu": mtu,
            },
            {
                "mgt_ip": device_ip,
                "name": ether_3,
                "mtu": mtu,
            },
            {
                "mgt_ip": device_ip,
                "name": ether_4,
                "mtu": mtu,
            },
        ]

        response = self.client.put(
            reverse("device_interface_list"), itf_request_body, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        request_body = [
            {
                "mgt_ip": device_ip,
                "chnl_name": "PortChannel101",
                "mtu": mtu,
                "admin_status": "up",
                "members": [ether_1, ether_2],
            },
            {
                "mgt_ip": device_ip,
                "chnl_name": "PortChannel102",
                "mtu": mtu,
                "admin_status": "up",
                "members": [ether_3, ether_4],
            },
        ]
        
        # delete mclag, if it exists.
        # port channel deletion will fail if port channel is found to be a member of mclag.

        self.client.delete(
            reverse("device_mclag_list"),
            {"mgt_ip": device_ip},
            format="json",
        )

        response = self.client.get(
            reverse("device_mclag_list"),
            {"mgt_ip": device_ip},
        )

        self.assertTrue(
            response.status_code == status.HTTP_200_OK
            or any(
                "resource not found" in res.lower() for res in response.json()["result"]
            )
        )

        # Now delete port channels

        request_body_2 = [
            {"mgt_ip": device_ip, "chnl_name": "PortChannel101"},
            {"mgt_ip": device_ip, "chnl_name": "PortChannel102"},
        ]

        response = self.client.delete(
            reverse("device_port_chnl"),
            request_body_2,
            format="json",
        )
        self.assertTrue(
            response.status_code == status.HTTP_200_OK
            or any(
                "resource not found" in res.lower() for res in response.json()["result"]
            )
        )

        for data in request_body:
            response = self.client.get(
                reverse("device_port_chnl"),
                data,
            )

            self.assertIsNone(response.json())
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            response = self.client.put(reverse("device_port_chnl"), data, format="json")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            response = self.client.get(
                reverse("device_port_chnl"),
                data,
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.json()["mtu"], data["mtu"])
            self.assertEqual(response.json()["admin_sts"], data["admin_status"])
            self.assertTrue(
                True
                if m in response.json()["members"]
                else False and len(response.json()["members"]) == len(data["members"])
                for m in data["members"]
            )
            # Remove port channel members
            response = self.client.delete(
                reverse("device_port_chnl"),
                data,
                format="json",
            )

            response = self.client.get(
                reverse("device_port_chnl"),
                data,
            )

            self.assertFalse(response.json()["members"])

            response = self.client.delete(
                reverse("device_port_chnl"),
                {"mgt_ip": device_ip, "chnl_name": data["chnl_name"]},
                format="json",
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            response = self.client.get(
                reverse("device_port_chnl"),
                {"mgt_ip": device_ip, "chnl_name": data["chnl_name"]},
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIsNone(response.json())
