"""
This module contains tests for the Interface API.
"""

from rest_framework import status
from network.test.test_common import ORCATest


class VlanTestCase(ORCATest):
    vlan_id = 1
    vlan_name = "Vlan1"

    """
    Test the VLAN API.
    """

    def test_vlan_config(self):
        device_ip = self.device_ips[0]
        response = self.del_req(
            "vlan_config", {"mgt_ip": device_ip, "name": self.vlan_name}
        )

        self.assertTrue(
            response.status_code == status.HTTP_200_OK
            or any(
                "resource not found" in res.lower() for res in response.json()["result"]
            )
        )

        response = self.get_req(
            "vlan_config", {"mgt_ip": device_ip, "name": self.vlan_name}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.json())

        response = self.put_req(
            "vlan_config",
            {"mgt_ip": device_ip, "name": self.vlan_name, "vlanid": self.vlan_id},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.get_req(
            "vlan_config", {"mgt_ip": device_ip, "name": self.vlan_name}
        )
        self.assertEqual(response.json()["name"], self.vlan_name)
        self.assertEqual(response.json()["vlanid"], self.vlan_id)

        response = self.del_req(
            "vlan_config", {"mgt_ip": device_ip, "name": self.vlan_name}
        )

        self.assertTrue(
            response.status_code == status.HTTP_200_OK
            or any(
                "resource not found" in res.lower() for res in response.json()["result"]
            )
        )

        response = self.get_req(
            "vlan_config", {"mgt_ip": device_ip, "name": self.vlan_name}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.json())

    def test_vlan_mem_config(self):
        device_ip = self.device_ips[0]
        ether_1 = self.ether_names[0]
        ether_2 = self.ether_names[1]

        response = self.del_req(
            "vlan_config", {"mgt_ip": device_ip, "name": self.vlan_name}
        )

        self.assertTrue(
            response.status_code == status.HTTP_200_OK
            or any(
                "resource not found" in res.lower() for res in response.json()["result"]
            )
        )

        response = self.get_req(
            "vlan_config", {"mgt_ip": device_ip, "name": self.vlan_name}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.json())

        request_body = {
            "mgt_ip": device_ip,
            "name": self.vlan_name,
            "vlanid": self.vlan_id,
            "members": {
                ether_1: "tagged",
                ether_2: "untagged",
            },
        }
        response = self.put_req(
            "vlan_config",
            request_body,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.get_req(
            "vlan_config", {"mgt_ip": device_ip, "name": self.vlan_name}
        )
        self.assertEqual(response.json()["name"], self.vlan_name)
        self.assertEqual(response.json()["vlanid"], self.vlan_id)
        self.assertTrue(
            all(
                True if m in response.json()["members"] else False
                for m in response.json()["members"]
            )
            and len(response.json()["members"]) == len(response.json()["members"])
        )
        self.assertEqual(response.json()["members"][ether_1], "tagged")
        self.assertEqual(response.json()["members"][ether_2], "untagged")
        
        response = self.del_req(
            "vlan_config", {"mgt_ip": device_ip, "name": self.vlan_name}
        )

        self.assertTrue(
            response.status_code == status.HTTP_200_OK
            or any(
                "resource not found" in res.lower() for res in response.json()["result"]
            )
        )

        response = self.get_req(
            "vlan_config", {"mgt_ip": device_ip, "name": self.vlan_name}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.json())
