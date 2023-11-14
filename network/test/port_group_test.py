"""
This module contains tests for the BGP API.
"""

from rest_framework import status

from network.test.test_common import ORCATest


class PortGroupTest(ORCATest):
    def test_port_group_speed_config(self):
        device_ip = self.device_ips[0]
        request_body = {"mgt_ip": device_ip, "port_group_id": "1", "speed": "SPEED_10G"}

        # Get current speed
        response = self.get_req("port_groups", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        orig_speed = response.json().get("speed")
        request_body["speed"] = self.get_speed_to_set(orig_speed)
        # Update speed
        response = self.put_req("port_groups", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        # Confirm changes
        response = self.get_req("port_groups", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        self.assertEqual(request_body["speed"], response.json().get("speed"))
        # Restore speed
        request_body["speed"] = orig_speed
        response = self.put_req("port_groups", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        # Confirm changes
        response = self.get_req("port_groups", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        self.assertEqual(request_body["speed"], response.json().get("speed"))
