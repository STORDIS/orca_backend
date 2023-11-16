"""
This module contains tests for the Interface API.
"""

from rest_framework import status
from network.test.test_common import ORCATest


class MclagTest(ORCATest):
    """
    This class contains tests for the Mclag API.
    """

    domain_id = 1
    mclag_sys_mac = "00:00:00:22:22:22"
    peer_link = "PortChannel100"
    mem_port_chnl = "PortChannel101"
    mem_port_chnl_2 = "PortChannel102"

    def test_mclag_config(self):
        device_ip_1 = self.device_ips[0]
        device_ip_2 = self.device_ips[1]
        self.del_req("device_mclag_list", {"mgt_ip": device_ip_1})
        response = self.get_req("device_mclag_list", {"mgt_ip": device_ip_1})

        self.assertTrue(
            response.status_code == status.HTTP_200_OK
            or any(
                "resource not found" in res.lower() for res in response.json()["result"]
            )
        )

        # Create peerlink port channel first
        req = {
            "mgt_ip": device_ip_1,
            "lag_name": self.peer_link,
        }
        self.perform_del_port_chnl(req)
        self.perform_add_port_chnl(req)

        request_body = {
            "mgt_ip": device_ip_1,
            "domain_id": self.domain_id,
            "source_address": device_ip_1,
            "peer_addr": device_ip_2,
            "peer_link": self.peer_link,
            "mclag_sys_mac": self.mclag_sys_mac,
        }

        response = self.put_req("device_mclag_list", request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.get_req(
            "device_mclag_list", {"mgt_ip": device_ip_1, "domain_id": self.domain_id}
        )

        self.assertEqual(response.json().get("domain_id"), self.domain_id)
        self.assertEqual(response.json().get("source_address"), device_ip_1)
        self.assertEqual(response.json().get("peer_addr"), device_ip_2)
        self.assertEqual(response.json().get("peer_link"), self.peer_link)
        self.assertEqual(response.json().get("mclag_sys_mac"), self.mclag_sys_mac)

        # Finally remove mclag

        self.del_req("device_mclag_list", {"mgt_ip": device_ip_1})

        response = self.get_req("device_mclag_list", {"mgt_ip": device_ip_1})

        self.assertTrue(
            response.status_code == status.HTTP_200_OK
            or any(
                "resource not found" in res.lower() for res in response.json()["result"]
            )
        )

    def test_mclag_member_config(self):
        device_ip_1 = self.device_ips[0]
        device_ip_2 = self.device_ips[1]

        response = self.del_req("device_mclag_list", {"mgt_ip": device_ip_1})
        self.assertTrue(
            response.status_code == status.HTTP_200_OK
            or any(
                "resource not found" in res.lower() for res in response.json()["result"]
            )
        )

        response = self.get_req("device_mclag_list", {"mgt_ip": device_ip_1})

        self.assertTrue(
            response.status_code == status.HTTP_200_OK and not response.json()
        )

        request_body = {
            "mgt_ip": device_ip_1,
            "domain_id": self.domain_id,
            "source_address": device_ip_1,
            "peer_addr": device_ip_2,
            "peer_link": self.peer_link,
            "mclag_sys_mac": self.mclag_sys_mac,
        }

        response = self.put_req("device_mclag_list", request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.get_req(
            "device_mclag_list", {"mgt_ip": device_ip_1, "domain_id": self.domain_id}
        )

        self.assertEqual(response.json().get("domain_id"), self.domain_id)
        self.assertEqual(response.json().get("source_address"), device_ip_1)
        self.assertEqual(response.json().get("peer_addr"), device_ip_2)
        self.assertEqual(response.json().get("peer_link"), self.peer_link)
        self.assertEqual(response.json().get("mclag_sys_mac"), self.mclag_sys_mac)

        request_body = [
            {
                "mgt_ip": device_ip_1,
                "lag_name": self.mem_port_chnl,
                "mtu": 8000,
                "admin_status": "up",
            },
            {
                "mgt_ip": device_ip_1,
                "lag_name": self.mem_port_chnl_2,
                "mtu": 9100,
                "admin_status": "up",
            },
        ]
        self.perform_del_port_chnl(request_body)
        self.perform_add_port_chnl(request_body)

        request_body_members = {
            "mgt_ip": device_ip_1,
            "domain_id": self.domain_id,
            "mclag_members": [self.mem_port_chnl, self.mem_port_chnl_2],
        }

        response = self.del_req("device_mclag_list", request_body_members)
        self.assertTrue(
            response.status_code == status.HTTP_200_OK
            or any(
                "resource not found" in res.lower() for res in response.json()["result"]
            )
        )
        response = self.put_req("device_mclag_list", request_body_members)
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        response = self.get_req("device_mclag_list", request_body_members)
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        self.assertEqual(len(response.json().get("mclag_members")), 2)
        for mem in response.json().get("mclag_members"):
            self.assertTrue(
                mem.get("lag_name") in [self.mem_port_chnl, self.mem_port_chnl_2]
            )
        
        # cleanup members
        response = self.del_req("device_mclag_list", request_body_members)
        self.assertTrue(
            response.status_code == status.HTTP_200_OK
            or any(
                "resource not found" in res.lower() for res in response.json()["result"]
            )
        )
        # cleanup mclag
        response = self.del_req("device_mclag_list", request_body)
        self.assertTrue(
            response.status_code == status.HTTP_200_OK
            or any(
                "resource not found" in res.lower() for res in response.json()["result"]
            )
        )

    def test_mclag_gateway_mac(self):
        device_ip_1 = self.device_ips[0]
        gw_mac = "aa:bb:aa:bb:aa:bb"
        self.del_req("mclag_gateway_mac", {"mgt_ip": device_ip_1})
        response = self.get_req(
            "mclag_gateway_mac", {"mgt_ip": device_ip_1, "gateway_mac": gw_mac}
        )
        self.assertTrue(
            response.status_code == status.HTTP_200_OK
            or any(
                "resource not found" in res.lower() for res in response.json()["result"]
            )
        )
        request_body = {
            "mgt_ip": device_ip_1,
            "gateway_mac": gw_mac,
        }
        response = self.put_req("mclag_gateway_mac", request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.get_req(
            "mclag_gateway_mac", {"mgt_ip": device_ip_1, "gateway_mac": gw_mac}
        )
        self.assertEqual(response.json().get("gateway_mac"), gw_mac)

        # Finally remove mclag gateway mac

        self.del_req("mclag_gateway_mac", {"mgt_ip": device_ip_1})
        response = self.get_req(
            "mclag_gateway_mac", {"mgt_ip": device_ip_1, "gateway_mac": gw_mac}
        )
        self.assertTrue(
            response.status_code == status.HTTP_200_OK
            or any(
                "resource not found" in res.lower() for res in response.json()["result"]
            )
        )
