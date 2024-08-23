"""
This module contains tests for the BGP API.
"""

import unittest
from rest_framework import status

from network.test.test_common import TestORCA


class TestBGP(TestORCA):
    """
    This class contains tests for the BGP API.
    """

    def test_bgp_global_config(self):
        """
        Test the BGP global configuration.

        This function tests the BGP global configuration by performing a series of
        API requests. It verifies that the configuration can be deleted, retrieved,
        modified, and deleted again, and that the expected values are returned.

        Args:
            self (TestCase): The test case object.

        Returns:
            None
        """
        device_ip = self.device_ips[0]
        request_body = {
            "mgt_ip": device_ip,
            "vrf_name": "default",
            "local_asn": 64500,
            "router_id": device_ip,
        }

        response = self.del_req("bgp_global", request_body)
        self.assertTrue(
            response.status_code == status.HTTP_200_OK
            or any(
                "resource not found" in res.get("message", "").lower() for res in response.json()["result"]
                if res != "\n"
            )
        )
        response = self.get_req("bgp_global", request_body)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(response.data)

        response = self.put_req("bgp_global", request_body)
        response = self.get_req("bgp_global", request_body)
        self.assertEqual(request_body.get("local_asn"), response.json()["local_asn"])
        self.assertEqual(request_body.get("vrf_name"), response.json()["vrf_name"])
        self.assertEqual(request_body.get("router_id"), response.json()["router_id"])

        response = self.del_req("bgp_global", request_body)
        self.assertTrue(
            response.status_code == status.HTTP_200_OK
            or any(
                "resource not found" in res.get("message", "").lower() for res in response.json()["result"]
                if res != "\n"
            )
        )
        response = self.get_req("bgp_global", request_body)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(response.data)

    @unittest.skip("Need to create neighbour first.")
    def test_bgp_nbr_config(self):
        """
        Test the BGP neighbor configuration.

        This function tests the BGP neighbor configuration by performing a series of
        API requests. It verifies that the neighbor is correctly added and that the
        expected response is received.

        Parameters:
        - self: The instance of the test class.

        Returns:
        None
        """
        for device_ip in self.device_ips:
            response = self.del_req(
                "bgp_global", {"mgt_ip": device_ip, "vrf_name": "default"}
            )
            self.assertTrue(
                response.status_code == status.HTTP_200_OK
                or any(
                    "resource not found" in res.get("message", "").lower()
                    for res in response.json()["result"]
                    if res != "\n"
                )
            )
            response = self.get_req("bgp_global", {"mgt_ip": device_ip})
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
            self.assertFalse(response.data)

        device_ip_1 = self.device_ips[0]
        request_body = {
            "mgt_ip": device_ip_1,
            "vrf_name": "default",
            "local_asn": 65000,
            "router_id": device_ip_1,
        }

        response = self.put_req("bgp_global", request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.get_req("bgp_global", request_body)
        self.assertEqual(request_body.get("local_asn"), response.json()["local_asn"])
        self.assertEqual(request_body.get("vrf_name"), response.json()["vrf_name"])
        self.assertEqual(request_body.get("router_id"), response.json()["router_id"])

        # Create neighbor BGP

        device_ip_2 = self.device_ips[1]
        request_body = {
            "mgt_ip": device_ip_2,
            "vrf_name": "default",
            "local_asn": 65001,
            "router_id": device_ip_2,
        }

        response = self.put_req("bgp_global", request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.get_req("bgp_global", request_body)
        self.assertEqual(request_body.get("local_asn"), response.json()["local_asn"])
        self.assertEqual(request_body.get("vrf_name"), response.json()["vrf_name"])
        self.assertEqual(request_body.get("router_id"), response.json()["router_id"])

        # Add neighbor BGP
        nbr_req = {
            "mgt_ip": device_ip_1,
            "remote_vrf": "default",
            "local_asn": 65000,
            "remote_asn": 65001,
            "neighbor_ip": "1.1.1.0",
        }

        response = self.del_req("bgp_nbr", nbr_req)
        self.assertTrue(
            response.status_code == status.HTTP_200_OK
            or any(
                "resource not found" in res.get("message", "").lower() for res in response.json()["result"]
                if res != "\n"
            )
        )
        response = self.get_req("bgp_nbr", nbr_req)
        self.assertFalse(response.json().get("nbr_sub_if"))
        self.assertFalse(response.json().get("nbr_bgp"))

        response = self.put_req("bgp_nbr", nbr_req)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.get_req("bgp_nbr", nbr_req)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json().get("nbr_sub_if")[0].get("ip_address"),
            nbr_req["neighbor_ip"],
        )
        self.assertEqual(
            response.json().get("nbr_bgp")[0].get("local_asn"), nbr_req["remote_asn"]
        )
        self.assertEqual(
            response.json().get("nbr_bgp")[0].get("vrf_name"), nbr_req["remote_vrf"]
        )

        response = self.del_req("bgp_nbr", nbr_req)
        self.assertTrue(
            response.status_code == status.HTTP_200_OK
            or any(
                "resource not found" in res.get("message", "").lower() for res in response.json()["result"]
                if res != "\n"
            )
        )

        response = self.del_req("bgp_global", request_body)
        self.assertTrue(
            response.status_code == status.HTTP_200_OK
            or any(
                "resource not found" in res.get("message", "").lower() for res in response.json()["result"]
                if res != "\n"
            )
        )
        response = self.get_req("bgp_global", request_body)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(response.data)

    def perform_add_bgp_global(self, request_body):
        # delete bgp config if it exists
        response = self.del_req("bgp_global", request_body)
        print(response.json())
        self.assertTrue(
            response.status_code == status.HTTP_200_OK
            or any(
                "resource not found" in res.get("message", "").lower() for res in response.json()["result"]
                if res != "\n"
            )
        )
        # verify bgp config is deleted
        response = self.get_req("bgp_global", request_body)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(response.data)

        # create bgp config
        response = self.put_req("bgp_global", request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # verify bgp config is created
        response = self.get_req("bgp_global", request_body)
        self.assertEqual(request_body.get("local_asn"), response.json()["local_asn"])
        self.assertEqual(request_body.get("vrf_name"), response.json()["vrf_name"])
        self.assertEqual(request_body.get("router_id"), response.json()["router_id"])

    def perform_delete_bgp_global(self, request_body):
        # delete bgp config
        response = self.del_req("bgp_global", request_body)
        self.assertTrue(
            response.status_code == status.HTTP_200_OK
            or any(
                "resource not found" in res.get("message", "").lower() for res in response.json()["result"]
                if res != "\n"
            )
        )
        response = self.get_req("bgp_global", request_body)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(response.data)

    def test_bgp_af_config(self):
        # configuring bgp global
        device_ip = self.device_ips[0]
        request_body = {
            "mgt_ip": device_ip,
            "vrf_name": "default",
            "local_asn": 64500,
            "router_id": device_ip,
        }

        self.perform_add_bgp_global(request_body)

        # adding bgp af
        request_body = {
            "mgt_ip": device_ip,
            "vrf_name": "default",
            "afi_safi": "ipv4_unicast",
            "max_ebgp_paths": 4,
        }
        response = self.put_req("bgp_af", request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # verify bgp af is created
        response = self.get_req("bgp_af", {
            "mgt_ip": device_ip, "local_asn": 64500, "afi_safi": "ipv4_unicast"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(request_body.get("afi_safi"), response.json()["afi_safi"])
        self.assertEqual(request_body.get("max_ebgp_paths"), response.json()["max_ebgp_paths"])
        self.assertEqual(request_body.get("vrf_name"), response.json()["vrf_name"])

        # delete bgp af config
        response = self.del_req("bgp_af", {"mgt_ip": device_ip})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.get_req("bgp_af", {
            "mgt_ip": device_ip, "local_asn": 64500, "afi_safi": "ipv4_unicast"
        })
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # delete bgp global config
        self.perform_delete_bgp_global({
            "mgt_ip": device_ip,
            "vrf_name": "default",
        })

    def test_bgp_af_update(self):
        # configuring bgp global
        device_ip = self.device_ips[0]
        request_body = {
            "mgt_ip": device_ip,
            "vrf_name": "default",
            "local_asn": 64500,
            "router_id": device_ip,
        }

        self.perform_add_bgp_global(request_body)

        # adding bgp af
        ipv4_request_body = {
            "mgt_ip": device_ip,
            "vrf_name": "default",
            "afi_safi": "ipv4_unicast",
            "max_ebgp_paths": 4,
        }
        response = self.put_req("bgp_af", ipv4_request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # verify bgp af is created
        response = self.get_req("bgp_af", {
            "mgt_ip": device_ip, "local_asn": 64500, "afi_safi": "ipv4_unicast"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ipv4_request_body.get("afi_safi"), response.json()["afi_safi"])
        self.assertEqual(ipv4_request_body.get("max_ebgp_paths"), response.json()["max_ebgp_paths"])
        self.assertEqual(ipv4_request_body.get("vrf_name"), response.json()["vrf_name"])

        # update bgp af adding new afi_safi
        ipv6_request_body = {
            "mgt_ip": device_ip,
            "vrf_name": "default",
            "afi_safi": "ipv6_unicast",
            "max_ebgp_paths": 4,
        }
        response = self.put_req("bgp_af", ipv6_request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # verify bgp af has both ipv4_unicast and ipv6_unicast
        response = self.get_req("bgp_af", {
            "mgt_ip": device_ip, "local_asn": 64500, "afi_safi": "ipv4_unicast"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ipv4_request_body.get("afi_safi"), response.json()["afi_safi"])
        self.assertEqual(ipv4_request_body.get("max_ebgp_paths"), response.json()["max_ebgp_paths"])
        self.assertEqual(ipv4_request_body.get("vrf_name"), response.json()["vrf_name"])

        response = self.get_req("bgp_af", {
            "mgt_ip": device_ip, "local_asn": 64500, "afi_safi": "ipv6_unicast"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ipv6_request_body.get("afi_safi"), response.json()["afi_safi"])
        self.assertEqual(ipv6_request_body.get("max_ebgp_paths"), response.json()["max_ebgp_paths"])
        self.assertEqual(ipv6_request_body.get("vrf_name"), response.json()["vrf_name"])

        # updating bgp af max_ebgp_paths to 8
        ipv6_request_body["max_ebgp_paths"] = 8
        response = self.put_req("bgp_af", ipv6_request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # verify bgp af is created
        response = self.get_req("bgp_af", {
            "mgt_ip": device_ip, "local_asn": 64500, "afi_safi": "ipv6_unicast"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ipv6_request_body.get("afi_safi"), response.json()["afi_safi"])
        self.assertEqual(ipv6_request_body.get("max_ebgp_paths"), response.json()["max_ebgp_paths"])
        self.assertEqual(ipv6_request_body.get("vrf_name"), response.json()["vrf_name"])

        # deleting bgp af
        response = self.del_req("bgp_af", {"mgt_ip": device_ip})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.get_req("bgp_af", {
            "mgt_ip": device_ip, "local_asn": 64500,
        })
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # delete bgp global config
        self.perform_delete_bgp_global({
            "mgt_ip": device_ip,
            "vrf_name": "default",
        })

    def test_bgp_af_delete(self):
        # configuring bgp global
        device_ip = self.device_ips[0]
        request_body = {
            "mgt_ip": device_ip,
            "vrf_name": "default",
            "local_asn": 64500,
            "router_id": device_ip,
        }

        self.perform_add_bgp_global(request_body)

        # adding bgp af network
        request_body = [
            {
                "mgt_ip": device_ip,
                "vrf_name": "default",
                "afi_safi": "ipv4_unicast",
            },
            {
                "mgt_ip": device_ip,
                "vrf_name": "default",
                "afi_safi": "ipv6_unicast",
            }
        ]
        response = self.put_req("bgp_af", request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # verify bgp af is created
        response = self.get_req("bgp_af", {
            "mgt_ip": device_ip, "local_asn": 64500, "afi_safi": "ipv4_unicast"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(request_body[0].get("afi_safi"), response.json()["afi_safi"])
        self.assertEqual(request_body[0].get("vrf_name"), response.json()["vrf_name"])

        response = self.get_req("bgp_af", {
            "mgt_ip": device_ip, "local_asn": 64500, "afi_safi": "ipv6_unicast"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(request_body[1].get("afi_safi"), response.json()["afi_safi"])
        self.assertEqual(request_body[1].get("vrf_name"), response.json()["vrf_name"])

        # deleting one bgp af
        response = self.del_req("bgp_af", {"mgt_ip": device_ip, "afi_safi": "ipv4_unicast", "vrf_name": "default"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # verify bgp af is deleted
        response = self.get_req("bgp_af", {
            "mgt_ip": device_ip, "local_asn": 64500, "afi_safi": "ipv4_unicast"
        })
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # verify bgp af ipv6_unicast is not deleted
        response = self.get_req("bgp_af", {
            "mgt_ip": device_ip, "local_asn": 64500, "afi_safi": "ipv6_unicast"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(request_body[1].get("afi_safi"), response.json()["afi_safi"])
        self.assertEqual(request_body[1].get("vrf_name"), response.json()["vrf_name"])

        # deleting bgp af all items
        response = self.del_req("bgp_af", {"mgt_ip": device_ip})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.get_req("bgp_af", {
            "mgt_ip": device_ip, "local_asn": 64500,
        })
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # delete bgp global config
        self.perform_delete_bgp_global({
            "mgt_ip": device_ip,
            "vrf_name": "default",
        })

    def test_bgp_af_network(self):
        # configuring bgp global
        device_ip = self.device_ips[0]
        request_body = {
            "mgt_ip": device_ip,
            "vrf_name": "default",
            "local_asn": 64500,
            "router_id": device_ip,
        }

        self.perform_add_bgp_global(request_body)

        # adding bgp af network
        ipv4_request_body = {
            "mgt_ip": device_ip,
            "vrf_name": "default",
            "afi_safi": "ipv4_unicast",
            "ip_prefix": "192.84.2.178/24",
        }
        response = self.put_req("bgp_af_network", ipv4_request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # verify bgp af is created
        response = self.get_req("bgp_af_network", {
            "mgt_ip": device_ip, "local_asn": 64500, "afi_safi": "ipv4_unicast"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(ipv4_request_body.get("afi_safi"), response.json()["afi_safi"])
        self.assertEqual(ipv4_request_body.get("ip_prefix"), response.json()["ip_prefix"])
        self.assertEqual(ipv4_request_body.get("vrf_name"), response.json()["vrf_name"])

        # deleting bgp af network
        response = self.del_req("bgp_af_network", {"mgt_ip": device_ip})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # verify bgp af network is deleted
        response = self.get_req("bgp_af_network", {
            "mgt_ip": device_ip, "local_asn": 64500, "afi_safi": "ipv4_unicast"
        })
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # delete bgp global config
        self.perform_delete_bgp_global({
            "mgt_ip": device_ip,
            "vrf_name": "default",
        })

    def test_bgp_af_network_update(self):
        # configuring bgp global
        device_ip = self.device_ips[0]
        request_body = {
            "mgt_ip": device_ip,
            "vrf_name": "default",
            "local_asn": 64500,
            "router_id": device_ip,
        }

        self.perform_add_bgp_global(request_body)

        # adding bgp af network
        ipv4_request_body = {
            "mgt_ip": device_ip,
            "vrf_name": "default",
            "afi_safi": "ipv4_unicast",
            "ip_prefix": "192.84.2.178/24",
        }
        response = self.put_req("bgp_af_network", ipv4_request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # verify bgp af is created
        response = self.get_req("bgp_af_network", {
            "mgt_ip": device_ip, "local_asn": 64500, "afi_safi": "ipv4_unicast"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(ipv4_request_body.get("afi_safi"), response.json()["afi_safi"])
        self.assertEqual(ipv4_request_body.get("ip_prefix"), response.json()["ip_prefix"])
        self.assertEqual(ipv4_request_body.get("vrf_name"), response.json()["vrf_name"])

        # update bgp af network
        ipv4_request_body = {
            "mgt_ip": device_ip,
            "vrf_name": "default",
            "afi_safi": "ipv6_unicast",
            "ip_prefix": "244.178.44.111/24",
        }
        response = self.put_req("bgp_af_network", ipv4_request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # verify bgp af is created
        response = self.get_req("bgp_af_network", {
            "mgt_ip": device_ip, "local_asn": 64500, "afi_safi": "ipv6_unicast"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ipv4_request_body.get("afi_safi"), response.json()["afi_safi"])
        self.assertEqual(ipv4_request_body.get("ip_prefix"), response.json()["ip_prefix"])
        self.assertEqual(ipv4_request_body.get("vrf_name"), response.json()["vrf_name"])

        # deleting bgp af network
        response = self.del_req("bgp_af_network", {"mgt_ip": device_ip})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # verify bgp af network is deleted
        response = self.get_req("bgp_af_network", {
            "mgt_ip": device_ip, "local_asn": 64500
        })
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # delete bgp global config
        self.perform_delete_bgp_global({
            "mgt_ip": device_ip,
            "vrf_name": "default",
        })

    def test_bgp_af_network_delete(self):
        # configuring bgp global
        device_ip = self.device_ips[0]
        request_body = {
            "mgt_ip": device_ip,
            "vrf_name": "default",
            "local_asn": 64500,
            "router_id": device_ip,
        }

        self.perform_add_bgp_global(request_body)

        # adding bgp af network
        request_body = [
            {
                "mgt_ip": device_ip,
                "vrf_name": "default",
                "afi_safi": "ipv4_unicast",
                "ip_prefix": "192.84.2.178/24",
            },
            {
                "mgt_ip": device_ip,
                "vrf_name": "default",
                "afi_safi": "ipv6_unicast",
                "ip_prefix": "244.178.44.111/24",
            }
        ]
        response = self.put_req("bgp_af_network", request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # verify bgp af network is created
        response = self.get_req("bgp_af_network", {
            "mgt_ip": device_ip, "local_asn": 64500, "afi_safi": "ipv4_unicast"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(request_body[0].get("afi_safi"), response.json()["afi_safi"])
        self.assertEqual(request_body[0].get("vrf_name"), response.json()["vrf_name"])
        self.assertEqual(request_body[0].get("ip_prefix"), response.json()["ip_prefix"])

        response = self.get_req("bgp_af_network", {
            "mgt_ip": device_ip, "local_asn": 64500, "afi_safi": "ipv6_unicast"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(request_body[1].get("afi_safi"), response.json()["afi_safi"])
        self.assertEqual(request_body[1].get("vrf_name"), response.json()["vrf_name"])
        self.assertEqual(request_body[1].get("ip_prefix"), response.json()["ip_prefix"])

        # deleting one bgp af network
        response = self.del_req("bgp_af_network", request_body[0])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # verify bgp af network ipv4_unicast is deleted
        response = self.get_req("bgp_af_network", {
            "mgt_ip": device_ip, "local_asn": 64500, "afi_safi": "ipv4_unicast"
        })
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # verify bgp af ipv6_unicast is not deleted
        response = self.get_req("bgp_af_network", {
            "mgt_ip": device_ip, "local_asn": 64500, "afi_safi": "ipv6_unicast"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(request_body[1].get("afi_safi"), response.json()["afi_safi"])
        self.assertEqual(request_body[1].get("vrf_name"), response.json()["vrf_name"])
        self.assertEqual(request_body[1].get("ip_prefix"), response.json()["ip_prefix"])

        # deleting bgp af all items
        response = self.del_req("bgp_af_network", {"mgt_ip": device_ip})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.get_req("bgp_af_network", {
            "mgt_ip": device_ip, "local_asn": 64500,
        })
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # delete bgp global config
        self.perform_delete_bgp_global({
            "mgt_ip": device_ip,
            "vrf_name": "default",
        })

    def test_bgp_af_aggregate_addr(self):
        # configuring bgp global
        device_ip = self.device_ips[0]
        request_body = {
            "mgt_ip": device_ip,
            "vrf_name": "default",
            "local_asn": 64500,
            "router_id": device_ip,
        }

        self.perform_add_bgp_global(request_body)

        # adding bgp af network
        ipv4_request_body = {
            "mgt_ip": device_ip,
            "vrf_name": "default",
            "afi_safi": "ipv4_unicast",
            "ip_prefix": "192.84.2.178/24",
        }
        response = self.put_req("bgp_af_aggregate_addr", ipv4_request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # verify bgp af is created
        response = self.get_req("bgp_af_aggregate_addr", {
            "mgt_ip": device_ip, "local_asn": 64500, "afi_safi": "ipv4_unicast"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(ipv4_request_body.get("afi_safi"), response.json()["afi_safi"])
        self.assertEqual(ipv4_request_body.get("ip_prefix"), response.json()["ip_prefix"])
        self.assertEqual(ipv4_request_body.get("vrf_name"), response.json()["vrf_name"])

        # deleting bgp af network
        response = self.del_req("bgp_af_aggregate_addr", {"mgt_ip": device_ip})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # verify bgp af network is deleted
        response = self.get_req("bgp_af_aggregate_addr", {
            "mgt_ip": device_ip, "local_asn": 64500, "afi_safi": "ipv4_unicast"
        })
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # delete bgp global config
        self.perform_delete_bgp_global({
            "mgt_ip": device_ip,
            "vrf_name": "default",
        })

    def test_bgp_af_aggregate_addr_update(self):
        # configuring bgp global
        device_ip = self.device_ips[0]
        request_body = {
            "mgt_ip": device_ip,
            "vrf_name": "default",
            "local_asn": 64500,
            "router_id": device_ip,
        }

        self.perform_add_bgp_global(request_body)

        # adding bgp af network
        ipv4_request_body = {
            "mgt_ip": device_ip,
            "vrf_name": "default",
            "afi_safi": "ipv4_unicast",
            "ip_prefix": "192.84.2.178/24",
        }
        response = self.put_req("bgp_af_aggregate_addr", ipv4_request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # verify bgp af is created
        response = self.get_req("bgp_af_aggregate_addr", {
            "mgt_ip": device_ip, "local_asn": 64500, "afi_safi": "ipv4_unicast"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(ipv4_request_body.get("afi_safi"), response.json()["afi_safi"])
        self.assertEqual(ipv4_request_body.get("ip_prefix"), response.json()["ip_prefix"])
        self.assertEqual(ipv4_request_body.get("vrf_name"), response.json()["vrf_name"])

        # updating bgp af network
        ipv6_request_body = {
            "mgt_ip": device_ip,
            "vrf_name": "default",
            "afi_safi": "ipv6_unicast",
            "ip_prefix": "244.178.44.111/24",
        }
        response = self.put_req("bgp_af_aggregate_addr", ipv6_request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # verify bgp af is created
        response = self.get_req("bgp_af_aggregate_addr", {
            "mgt_ip": device_ip, "local_asn": 64500, "afi_safi": "ipv6_unicast"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(ipv6_request_body.get("afi_safi"), response.json()["afi_safi"])
        self.assertEqual(ipv6_request_body.get("ip_prefix"), response.json()["ip_prefix"])
        self.assertEqual(ipv6_request_body.get("vrf_name"), response.json()["vrf_name"])

        # verifying previous item
        response = self.get_req("bgp_af_aggregate_addr", {
            "mgt_ip": device_ip, "local_asn": 64500, "afi_safi": "ipv4_unicast"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(ipv4_request_body.get("afi_safi"), response.json()["afi_safi"])
        self.assertEqual(ipv4_request_body.get("ip_prefix"), response.json()["ip_prefix"])
        self.assertEqual(ipv4_request_body.get("vrf_name"), response.json()["vrf_name"])

        # deleting bgp af aggregate addr
        response = self.del_req("bgp_af_aggregate_addr", {"mgt_ip": device_ip})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # verify bgp af aggregate addr is deleted
        response = self.get_req("bgp_af_aggregate_addr", {
            "mgt_ip": device_ip, "local_asn": 64500,
        })
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # delete bgp global config
        self.perform_delete_bgp_global({
            "mgt_ip": device_ip,
            "vrf_name": "default",
        })

    def test_bgp_af_aggregate_addr_delete(self):
        # configuring bgp global
        device_ip = self.device_ips[0]
        request_body = {
            "mgt_ip": device_ip,
            "vrf_name": "default",
            "local_asn": 64500,
            "router_id": device_ip,
        }

        self.perform_add_bgp_global(request_body)

        # adding bgp af aggregate addr
        request_body = [
            {
                "mgt_ip": device_ip,
                "vrf_name": "default",
                "afi_safi": "ipv4_unicast",
                "ip_prefix": "192.84.2.178/24",
            },
            {
                "mgt_ip": device_ip,
                "vrf_name": "default",
                "afi_safi": "ipv6_unicast",
                "ip_prefix": "244.178.44.111/24",
            }
        ]
        response = self.put_req("bgp_af_aggregate_addr", request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # verify bgp af network is created
        response = self.get_req("bgp_af_aggregate_addr", {
            "mgt_ip": device_ip, "local_asn": 64500, "afi_safi": "ipv4_unicast"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(request_body[0].get("afi_safi"), response.json()["afi_safi"])
        self.assertEqual(request_body[0].get("vrf_name"), response.json()["vrf_name"])
        self.assertEqual(request_body[0].get("ip_prefix"), response.json()["ip_prefix"])

        response = self.get_req("bgp_af_aggregate_addr", {
            "mgt_ip": device_ip, "local_asn": 64500, "afi_safi": "ipv6_unicast"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(request_body[1].get("afi_safi"), response.json()["afi_safi"])
        self.assertEqual(request_body[1].get("vrf_name"), response.json()["vrf_name"])
        self.assertEqual(request_body[1].get("ip_prefix"), response.json()["ip_prefix"])

        # deleting one bgp af network
        response = self.del_req("bgp_af_aggregate_addr", request_body[0])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # verify bgp af network ipv4_unicast is deleted
        response = self.get_req("bgp_af_aggregate_addr", {
            "mgt_ip": device_ip, "local_asn": 64500, "afi_safi": "ipv4_unicast"
        })
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # verify bgp af ipv6_unicast is not deleted
        response = self.get_req("bgp_af_aggregate_addr", {
            "mgt_ip": device_ip, "local_asn": 64500, "afi_safi": "ipv6_unicast"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(request_body[1].get("afi_safi"), response.json()["afi_safi"])
        self.assertEqual(request_body[1].get("vrf_name"), response.json()["vrf_name"])
        self.assertEqual(request_body[1].get("ip_prefix"), response.json()["ip_prefix"])

        # deleting bgp af all items
        response = self.del_req("bgp_af_aggregate_addr", {"mgt_ip": device_ip})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.get_req("bgp_af_aggregate_addr", {
            "mgt_ip": device_ip, "local_asn": 64500,
        })
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # delete bgp global config
        self.perform_delete_bgp_global({
            "mgt_ip": device_ip,
            "vrf_name": "default",
        })
