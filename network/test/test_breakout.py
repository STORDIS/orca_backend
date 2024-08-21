from rest_framework import status

from network.test.test_common import TestORCA
from orca_nw_lib.utils import get_component_name_from_if_alias


class TestBreakout(TestORCA):

    def test_breakout_config(self):
        device_ip = self.device_ips[0]

        # adding interface member
        ether_1 = "Ethernet56"
        itf_request_body = [
            {
                "mgt_ip": device_ip,
                "name": ether_1,
                "mtu": 9100,
            },
        ]
        self.assert_with_timeout_retry(
            lambda path, payload: self.put_req(path, payload),
            "device_interface_list",
            itf_request_body,
            status=status.HTTP_200_OK,
        )

        interface = self.get_req("device_interface_list", {"mgt_ip": device_ip, "name": ether_1})
        interface_alias = interface.json()["alias"]

        # adding breakout configuration

        request_body = {
            "mgt_ip": "10.10.229.105",
            "if_name": ether_1,
            "if_alias": interface_alias,
            "breakout_speed": "SPEED_50GB",
            "index": 1,
            "num_breakouts": 2,
            "num_physical_channels": 0
        }

        response = self.put_req("breakout", request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.get_req("breakout", {"mgt_ip": "10.10.229.105", "if_name": ether_1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["breakout_mode"], "2x50G")
        self.assertEqual(response.json()["port"], get_component_name_from_if_alias(if_alias=interface_alias))
        self.assertTrue(response.json()["status"] in ["InProgress", "Completed"])

        # removing breakout configuration
        response = self.del_req("breakout", {"mgt_ip": "10.10.229.105", "if_name": ether_1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.get_req("breakout", {"mgt_ip": "10.10.229.105", "if_name": ether_1})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # removing interface member
        response = self.del_req("device_interface_list", itf_request_body)
        self.assertTrue(
            response.status_code == status.HTTP_200_OK
            or any(
                "resource not found" in res.get("message", "").lower() for res in response.json()["result"]
                if res != "\n"
            )
        )

    def test_breakout_update(self):
        device_ip = self.device_ips[0]

        # adding interface member
        ether_1 = "Ethernet56"
        itf_request_body = [
            {
                "mgt_ip": device_ip,
                "name": ether_1,
                "mtu": 9100,
            },
        ]
        self.assert_with_timeout_retry(
            lambda path, payload: self.put_req(path, payload),
            "device_interface_list",
            itf_request_body,
            status=status.HTTP_200_OK,
        )

        interface = self.get_req("device_interface_list", {"mgt_ip": device_ip, "name": ether_1})
        interface_alias = interface.json()["alias"]

        # adding breakout configuration

        request_body = {
            "mgt_ip": "10.10.229.105",
            "if_name": ether_1,
            "if_alias": interface_alias,
            "breakout_speed": "SPEED_50GB",
            "index": 1,
            "num_breakouts": 2,
            "num_physical_channels": 0
        }

        response = self.put_req("breakout", request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.get_req("breakout", {"mgt_ip": "10.10.229.105", "if_name": ether_1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["breakout_mode"], "2x50G")
        self.assertEqual(response.json()["port"], get_component_name_from_if_alias(if_alias=interface_alias))
        self.assertTrue(response.json()["status"] in ["InProgress", "Completed"])

        # updating breakout configuration
        request_body["breakout_speed"] = "SPEED_25GB"
        request_body["num_breakouts"] = 4
        response = self.put_req("breakout", request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.get_req("breakout", {"mgt_ip": "10.10.229.105", "if_name": ether_1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["breakout_mode"], "4x25G")
        self.assertEqual(response.json()["port"], get_component_name_from_if_alias(if_alias=interface_alias))
        self.assertTrue(response.json()["status"] in ["InProgress", "Completed"])

        # removing breakout configuration
        response = self.del_req("breakout", {"mgt_ip": "10.10.229.105", "if_name": ether_1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.get_req("breakout", {"mgt_ip": "10.10.229.105", "if_name": ether_1})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # removing interface member
        response = self.del_req("device_interface_list", itf_request_body)
        self.assertTrue(
            response.status_code == status.HTTP_200_OK
            or any(
                "resource not found" in res.get("message", "").lower() for res in response.json()["result"]
                if res != "\n"
            )
        )
