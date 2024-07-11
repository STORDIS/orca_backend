"""
This module contains tests for the Interface API.
"""

from rest_framework import status
from network.test.test_common import TestORCA


class TestMclag(TestORCA):
    """
    This class contains tests for the Mclag API.
    """

    domain_id = 1
    mclag_sys_mac = "00:00:00:22:22:22"
    peer_link = "PortChannel100"
    mem_port_chnl = "PortChannel101"
    mem_port_chnl_2 = "PortChannel102"

    def test_mclag_config(self):
        """
        Test the MCLAG configuration.

        This function tests the MCLAG configuration by performing a series of operations
        including creating a peerlink port channel, configuring MCLAG settings on a device,
        and checking the response of each operation. The function takes no parameters and
        does not return anything.

        :return: None
        """
        device_ip_1 = self.device_ips[0]
        device_ip_2 = self.device_ips[1]
        response = self.del_req("device_mclag_list", {"mgt_ip": device_ip_1})

        self.assertTrue(
            response.status_code == status.HTTP_200_OK
            or any(
                "resource not found" in res.get("message", "").lower()
                for res in response.json()["result"]
                if res != "\n"
            )
        )
        response = self.get_req("device_mclag_list", {"mgt_ip": device_ip_1})
        self.assertTrue(response.status_code == status.HTTP_204_NO_CONTENT)
        self.assertFalse(response.data)

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
        self.remove_mclag(device_ip_1)

    def test_mclag_delay_restore(self):
        device_ip_1 = self.device_ips[0]

        # create mclag with only domain id and delay_restore
        request_body = {
            "mgt_ip": device_ip_1,
            "domain_id": self.domain_id,
            "delay_restore": 300,
        }

        response = self.put_req("device_mclag_list", request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.get_req(
            "device_mclag_list", {"mgt_ip": device_ip_1, "domain_id": self.domain_id}
        )

        self.assertEqual(response.json().get("domain_id"), self.domain_id)
        self.assertEqual(
            response.json().get("delay_restore"), request_body["delay_restore"]
        )

        # update delay_restore
        request_body = {
            "mgt_ip": device_ip_1,
            "domain_id": self.domain_id,
            "delay_restore": 400,
        }

        response = self.put_req("device_mclag_list", request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.get_req(
            "device_mclag_list", {"mgt_ip": device_ip_1, "domain_id": self.domain_id}
        )

        self.assertEqual(response.json().get("domain_id"), self.domain_id)
        self.assertEqual(
            response.json().get("delay_restore"), request_body["delay_restore"]
        )

        self.remove_mclag(device_ip_1)

    def test_mclag_session_timeout(self):
        device_ip_1 = self.device_ips[0]
        # create mclag with only domain id and session_timeout
        request_body = {
            "mgt_ip": device_ip_1,
            "domain_id": self.domain_id,
            "session_timeout": 30,
        }

        response = self.put_req("device_mclag_list", request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.get_req(
            "device_mclag_list", {"mgt_ip": device_ip_1, "domain_id": self.domain_id}
        )

        self.assertEqual(response.json().get("domain_id"), self.domain_id)
        self.assertEqual(
            response.json().get("session_timeout"), request_body["session_timeout"]
        )

        # update session timeout
        request_body = {
            "mgt_ip": device_ip_1,
            "domain_id": self.domain_id,
            "session_timeout": 60,
        }

        response = self.put_req("device_mclag_list", request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.get_req(
            "device_mclag_list", {"mgt_ip": device_ip_1, "domain_id": self.domain_id}
        )

        self.assertEqual(response.json().get("domain_id"), self.domain_id)
        self.assertEqual(
            response.json().get("session_timeout"), request_body["session_timeout"]
        )
        self.remove_mclag(device_ip_1)

    def test_mclag_keepalive_interval(self):
        device_ip_1 = self.device_ips[0]
        # create mclag with only domain id and keepalive_interval
        request_body = {
            "mgt_ip": device_ip_1,
            "domain_id": self.domain_id,
            "keepalive_interval": 1,
        }

        response = self.put_req("device_mclag_list", request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.get_req(
            "device_mclag_list", {"mgt_ip": device_ip_1, "domain_id": self.domain_id}
        )

        self.assertEqual(response.json().get("domain_id"), self.domain_id)
        self.assertEqual(
            response.json().get("keepalive_interval"),
            request_body["keepalive_interval"],
        )

        # update keepalive_interval
        request_body = {
            "mgt_ip": device_ip_1,
            "domain_id": self.domain_id,
            "keepalive_interval": 1,
        }

        response = self.put_req("device_mclag_list", request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.get_req(
            "device_mclag_list", {"mgt_ip": device_ip_1, "domain_id": self.domain_id}
        )

        self.assertEqual(response.json().get("domain_id"), self.domain_id)
        self.assertEqual(
            response.json().get("keepalive_interval"),
            request_body["keepalive_interval"],
        )

        self.remove_mclag(device_ip_1)

    def test_mclag_member_config(self):
        """
        Test the MCLAG member configuration.

        This function tests the MCLAG member configuration by performing a series of operations
        including creating a peerlink port channel, configuring MCLAG settings on a device,
        and checking the response of each operation. The function takes no parameters and
        does not return anything.

        :return: None
        """
        device_ip_1 = self.device_ips[0]
        device_ip_2 = self.device_ips[1]

        response = self.del_req("device_mclag_list", {"mgt_ip": device_ip_1})

        self.assertTrue(
            response.status_code == status.HTTP_200_OK
            or any(
                "resource not found" in res.get("message", "").lower()
                for res in response.json()["result"]
                if res != "\n"
            )
        )

        response = self.get_req("device_mclag_list", {"mgt_ip": device_ip_1})
        self.assertTrue(response.status_code == status.HTTP_204_NO_CONTENT)
        self.assertFalse(response.data)

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
                "resource not found" in res.get("message", "").lower()
                for res in response.json()["result"]
                if res != "\n"
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
        print("---", response)
        self.assertTrue(
            response.status_code == status.HTTP_200_OK
            or any(
                "resource not found" in res.get("message", "").lower()
                for res in response.json()["result"]
                if res != "\n"
            )
        )
        # cleanup mclag
        response = self.del_req("device_mclag_list", request_body)
        self.assertTrue(
            response.status_code == status.HTTP_200_OK
            or any(
                "resource not found" in res.get("message", "").lower()
                for res in response.json()["result"]
                if res != "\n"
            )
        )

    def test_mclag_gateway_mac(self):
        """
        Test the MCLAG gateway MAC configuration.

        This function tests the MCLAG gateway MAC configuration by performing a series of operations
        including creating a peerlink port channel, configuring MCLAG settings on a device,
        and checking the response of each operation. The function takes no parameters and
        does not return anything.

        :return: None
        """

        device_ip_1 = self.device_ips[0]
        gw_mac = "aa:bb:aa:bb:aa:bb"
        response = self.del_req("mclag_gateway_mac", {"mgt_ip": device_ip_1})
        self.assertTrue(
            response.status_code == status.HTTP_200_OK
            or any(
                "resource not found" in res.get("message", "").lower()
                for res in response.json()["result"]
                if res != "\n"
            )
        )
        response = self.get_req(
            "mclag_gateway_mac", {"mgt_ip": device_ip_1, "gateway_mac": gw_mac}
        )
        self.assertTrue(response.status_code == status.HTTP_204_NO_CONTENT)
        self.assertFalse(response.data)

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

        response = self.del_req("mclag_gateway_mac", {"mgt_ip": device_ip_1})
        self.assertTrue(
            response.status_code == status.HTTP_200_OK
            or any(
                "resource not found" in res.get("message", "").lower()
                for res in response.json()["result"]
                if res != "\n"
            )
        )

        response = self.get_req(
            "mclag_gateway_mac", {"mgt_ip": device_ip_1, "gateway_mac": gw_mac}
        )
        self.assertTrue(response.status_code == status.HTTP_204_NO_CONTENT)
        self.assertFalse(response.data)

    def test_mclag_domain_fast_convergence(self):
        device_ip_1 = self.device_ips[0]
        device_ip_2 = self.device_ips[1]
        response = self.del_req("device_mclag_list", {"mgt_ip": device_ip_1})

        self.assertTrue(
            response.status_code == status.HTTP_200_OK
            or any(
                "resource not found" in res.get("message", "").lower()
                for res in response.json()["result"]
                if res != "\n"
            )
        )
        response = self.get_req("device_mclag_list", {"mgt_ip": device_ip_1})
        self.assertTrue(response.status_code == status.HTTP_204_NO_CONTENT)
        self.assertFalse(response.data)

        # Create peerlink port channel first
        req = {
            "mgt_ip": device_ip_1,
            "lag_name": self.peer_link,
        }
        self.perform_del_port_chnl(req)
        self.perform_add_port_chnl(req)

        # body for testing fast convergence
        request_body = {
            "mgt_ip": device_ip_1,
            "domain_id": self.domain_id,
            "source_address": device_ip_1,
            "peer_addr": device_ip_2,
            "peer_link": self.peer_link,
            "mclag_sys_mac": self.mclag_sys_mac,
            "fast_convergence": "enable",
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
        self.assertEqual(response.json().get("fast_convergence"), "enable")

        # updating to remove fast convergence

        request_body = {
            "mgt_ip": device_ip_1,
            "domain_id": self.domain_id,
            "source_address": device_ip_1,
            "peer_addr": device_ip_2,
            "peer_link": self.peer_link,
            "mclag_sys_mac": self.mclag_sys_mac,
            "fast_convergence": "disable",
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
        self.assertIsNone(response.json().get("fast_convergence"))

        # Finally remove mclag
        self.remove_mclag(device_ip_1)

    def test_config_mclag_domain_fast_convergence(self):
        device_ip_1 = self.device_ips[0]
        device_ip_2 = self.device_ips[1]
        response = self.del_req("device_mclag_list", {"mgt_ip": device_ip_1})

        self.assertTrue(
            response.status_code == status.HTTP_200_OK
            or any(
                "resource not found" in res.get("message", "").lower()
                for res in response.json()["result"]
                if res != "\n"
            )
        )
        response = self.get_req("device_mclag_list", {"mgt_ip": device_ip_1})
        self.assertTrue(response.status_code == status.HTTP_204_NO_CONTENT)
        self.assertFalse(response.data)

        # Create peerlink port channel first
        req = {
            "mgt_ip": device_ip_1,
            "lag_name": self.peer_link,
        }
        self.perform_del_port_chnl(req)
        self.perform_add_port_chnl(req)

        # body for testing
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

        # enableing fast convergence using new api

        response = self.post_req(
            url_name="config_mclag_fast_convergence",
            req_json={
                "mgt_ip": device_ip_1,
                "domain_id": self.domain_id,
                "fast_convergence": "enable",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.get_req(
            "device_mclag_list", {"mgt_ip": device_ip_1, "domain_id": self.domain_id}
        )
        self.assertEqual(response.json().get("fast_convergence"), "enable")

        # enableing fast convergence using new api

        response = self.post_req(
            url_name="config_mclag_fast_convergence",
            req_json={
                "mgt_ip": device_ip_1,
                "domain_id": self.domain_id,
                "fast_convergence": "disable",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.get_req(
            "device_mclag_list", {"mgt_ip": device_ip_1, "domain_id": self.domain_id}
        )
        self.assertIsNone(response.json().get("fast_convergence"))

        # Finally remove mclag
        self.remove_mclag(device_ip_1)
