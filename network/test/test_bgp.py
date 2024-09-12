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

    def test_bgp_different_router_id(self):
        device_ip = self.device_ips[0]
        request_body = {
            "mgt_ip": device_ip,
            "vrf_name": "default",
            "local_asn": 64500,
            "router_id": "192.10.10.8",
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

    def test_bgp_neighbor_config(self):
        device_ip = self.device_ips[0]
        request_body = {
            "mgt_ip": device_ip,
            "vrf_name": "default",
            "local_asn": 64500,
            "router_id": device_ip,
        }

        # configuring bgp global
        self.perform_add_bgp_global(request_body)

        nbr_req = {
            "mgt_ip": device_ip,
            "remote_asn": 65100,
            "vrf_name": "default",
            "neighbor_ip": "1.1.1.1"
        }

        # delete bgp neighbor config if it exists
        self.assert_response_status(
            self.del_req("bgp_nbr", nbr_req),
            status.HTTP_200_OK,
            "resource not found",
        )
        response = self.get_req("bgp_nbr", nbr_req)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # add bgp neighbor config
        response = self.put_req("bgp_nbr", nbr_req)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.get_req("bgp_nbr", nbr_req)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(nbr_req.get("neighbor_ip"), response.json()["neighbor_ip"])
        self.assertEqual(nbr_req.get("remote_asn"), response.json()["remote_asn"])
        self.assertEqual(nbr_req.get("vrf_name"), response.json()["vrf_name"])

        # clean up
        response = self.del_req("bgp_nbr", nbr_req)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.get_req("bgp_nbr", nbr_req)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.perform_delete_bgp_global(request_body)

    def test_bgp_nbr_af_config(self):
        device_ip = self.device_ips[0]
        request_body = {
            "mgt_ip": device_ip,
            "vrf_name": "default",
            "local_asn": 64500,
            "router_id": device_ip,
        }

        # configuring bgp global
        self.perform_add_bgp_global(request_body)

        nbr_req = {
            "mgt_ip": device_ip,
            "remote_asn": 65100,
            "vrf_name": "default",
            "neighbor_ip": "1.1.1.1"
        }

        # delete bgp neighbor config if it exists
        self.assert_response_status(
            self.del_req("bgp_nbr", nbr_req),
            status.HTTP_200_OK,
            "resource not found",
        )
        response = self.get_req("bgp_nbr", nbr_req)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # add bgp neighbor config
        response = self.put_req("bgp_nbr", nbr_req)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.get_req("bgp_nbr", nbr_req)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(nbr_req.get("neighbor_ip"), response.json()["neighbor_ip"])
        self.assertEqual(nbr_req.get("remote_asn"), response.json()["remote_asn"])
        self.assertEqual(nbr_req.get("vrf_name"), response.json()["vrf_name"])

        # configuring bgp af
        request_body = {
            "mgt_ip": device_ip,
            "afi_safi": "ipv4_unicast",
            "vrf_name": "default",
            "neighbor_ip": "1.1.1.1",
        }

        response = self.put_req("bgp_nbr_af", request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.get_req("bgp_nbr_af", request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(request_body.get("afi_safi"), response.json()["afi_safi"])
        self.assertEqual(request_body.get("vrf_name"), response.json()["vrf_name"])
        self.assertEqual(request_body.get("neighbor_ip"), response.json()["neighbor_ip"])

        # clean up
        response = self.del_req("bgp_nbr_af", request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.get_req("bgp_nbr_af", request_body)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.del_req("bgp_nbr", nbr_req)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.get_req("bgp_nbr", nbr_req)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.perform_delete_bgp_global(request_body)

    def test_bgp_ngr_multiple_af(self):
        device_ip = self.device_ips[0]
        request_body = {
            "mgt_ip": device_ip,
            "vrf_name": "default",
            "local_asn": 64500,
            "router_id": device_ip,
        }

        # configuring bgp global
        self.perform_add_bgp_global(request_body)

        nbr_req = {
            "mgt_ip": device_ip,
            "remote_asn": 65100,
            "vrf_name": "default",
            "neighbor_ip": "1.1.1.1"
        }

        # delete bgp neighbor config if it exists
        self.assert_response_status(
            self.del_req("bgp_nbr", nbr_req),
            status.HTTP_200_OK,
            "resource not found",
        )
        response = self.get_req("bgp_nbr", nbr_req)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # add bgp neighbor config
        response = self.put_req("bgp_nbr", nbr_req)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.get_req("bgp_nbr", nbr_req)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(nbr_req.get("neighbor_ip"), response.json()["neighbor_ip"])
        self.assertEqual(nbr_req.get("remote_asn"), response.json()["remote_asn"])
        self.assertEqual(nbr_req.get("vrf_name"), response.json()["vrf_name"])

        # configuring bgp af
        nbr_af_body = [
            {
                "mgt_ip": device_ip,
                "afi_safi": "ipv4_unicast",
                "vrf_name": "default",
                "neighbor_ip": "1.1.1.1",
            },
            {
                "mgt_ip": device_ip,
                "afi_safi": "ipv6_unicast",
                "vrf_name": "default",
                "neighbor_ip": "1.1.1.1",
            }
        ]

        response = self.put_req("bgp_nbr_af", nbr_af_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.get_req("bgp_nbr_af", {
            "mgt_ip": device_ip, "neighbor_ip": "1.1.1.1", "afi_safi": "ipv4_unicast"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(nbr_af_body[0].get("afi_safi"), response.json()["afi_safi"])
        self.assertEqual(nbr_af_body[0].get("vrf_name"), response.json()["vrf_name"])
        self.assertEqual(nbr_af_body[0].get("neighbor_ip"), response.json()["neighbor_ip"])

        response = self.get_req("bgp_nbr_af", {
            "mgt_ip": device_ip, "neighbor_ip": "1.1.1.1", "afi_safi": "ipv6_unicast"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(nbr_af_body[1].get("afi_safi"), response.json()["afi_safi"])
        self.assertEqual(nbr_af_body[1].get("vrf_name"), response.json()["vrf_name"])
        self.assertEqual(nbr_af_body[1].get("neighbor_ip"), response.json()["neighbor_ip"])

        # clean up
        response = self.del_req("bgp_nbr_af", {
            "mgt_ip": device_ip, "neighbor_ip": "1.1.1.1",
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.get_req("bgp_nbr_af", {
            "mgt_ip": device_ip, "neighbor_ip": "1.1.1.1",
        })
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.del_req("bgp_nbr", nbr_req)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.get_req("bgp_nbr", nbr_req)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.perform_delete_bgp_global(request_body)

    def test_bgp_neighbor_bgp(self):
        device_ip = self.device_ips[0]
        asn = 64500
        request_body = {
            "mgt_ip": device_ip,
            "vrf_name": "default",
            "local_asn": asn,
            "router_id": device_ip,
        }

        # configuring bgp global
        self.perform_add_bgp_global(request_body)

        nbr_req = {
            "mgt_ip": device_ip,
            "remote_asn": asn,
            "vrf_name": "default",
            "neighbor_ip": "1.1.1.1"
        }

        # delete bgp neighbor config if it exists
        self.assert_response_status(
            self.del_req("bgp_nbr", nbr_req),
            status.HTTP_200_OK,
            "resource not found",
        )
        response = self.get_req("bgp_nbr", nbr_req)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # add bgp neighbor config
        response = self.put_req("bgp_nbr", nbr_req)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.get_req("bgp_nbr", nbr_req)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(nbr_req.get("neighbor_ip"), response.json()["neighbor_ip"])
        self.assertEqual(nbr_req.get("remote_asn"), response.json()["remote_asn"])
        self.assertEqual(nbr_req.get("vrf_name"), response.json()["vrf_name"])

        response = self.get_req("bgp_nbr_remote_bgp", {
            "mgt_ip": device_ip, "neighbor_ip": "1.1.1.1", "asn": asn
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(request_body.get("local_asn"), response.json()["local_asn"])
        self.assertEqual(request_body.get("vrf_name"), response.json()["vrf_name"])
        self.assertEqual(request_body.get("router_id"), response.json()["router_id"])

        # clean up
        response = self.del_req("bgp_nbr", nbr_req)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.get_req("bgp_nbr", nbr_req)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.perform_delete_bgp_global(request_body)

    def test_bgp_sub_interface(self):
        device_ip = self.device_ips[0]
        ether_name = self.ether_names[1]
        ip = "10.10.100.1"
        prefix_len = 24
        response = self.get_req(
            "device_interface_list", {"mgt_ip": device_ip, "name": ether_name}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        intf_request_body = {
            "mgt_ip": device_ip,
            "name": ether_name,
            "ip_address": f"{ip}/{prefix_len}",
        }
        self.assert_with_timeout_retry(
            lambda path, data: self.put_req(path, data),
            "device_interface_list",
            intf_request_body,
            status=status.HTTP_200_OK,
        )

        # verifying the ip_address value
        response = self.get_req("subinterface", {"mgt_ip": device_ip, "name": ether_name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_body = response.json()
        if isinstance(response_body, list):
            self.assertTrue(any([i["ip_address"] == ip for i in response_body]))
        else:
            self.assertEqual(response_body["ip_address"], ip)

        asn = 64500
        request_body = {
            "mgt_ip": device_ip,
            "vrf_name": "default",
            "local_asn": asn,
            "router_id": device_ip,
        }

        # configuring bgp global
        self.perform_add_bgp_global(request_body)

        nbr_req = {
            "mgt_ip": device_ip,
            "remote_asn": asn,
            "vrf_name": "default",
            "neighbor_ip": ip
        }

        # delete bgp neighbor config if it exists
        self.assert_response_status(
            self.del_req("bgp_nbr", nbr_req),
            status.HTTP_200_OK,
            "resource not found",
        )
        response = self.get_req("bgp_nbr", nbr_req)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # add bgp neighbor config
        response = self.put_req("bgp_nbr", nbr_req)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.get_req("bgp_nbr", nbr_req)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(nbr_req.get("neighbor_ip"), response.json()["neighbor_ip"])
        self.assertEqual(nbr_req.get("remote_asn"), response.json()["remote_asn"])
        self.assertEqual(nbr_req.get("vrf_name"), response.json()["vrf_name"])

        response = self.get_req("bgp_nbr_subinterface", {
            "mgt_ip": device_ip, "neighbor_ip": ip,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_body = response.json()
        if isinstance(response_body, list):
            self.assertTrue(any([i["ip_address"] == ip for i in response_body]))
        else:
            self.assertEqual(response_body["ip_address"], ip)

        # clean up
        response = self.del_req("subinterface", intf_request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # verifying the ip_address deletion
        response = self.get_req("subinterface", {"mgt_ip": device_ip, "name": ether_name})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.del_req("bgp_nbr", nbr_req)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.get_req("bgp_nbr", nbr_req)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.perform_delete_bgp_global(request_body)

    def test_bgp_neighbors_remote_bgp(self):
        device_ip_1 = self.device_ips[0]
        device_ip_2 = self.device_ips[1]

        device_1_asn = 64500
        device_2_asn = 64501

        neighbor_ip_1 = "1.1.1.1"

        bgp_request_body = [{
            "mgt_ip": device_ip_1,
            "vrf_name": "default",
            "local_asn": device_1_asn,
            "router_id": device_ip_1,
        }, {
            "mgt_ip": device_ip_2,
            "vrf_name": "default",
            "local_asn": device_2_asn,
            "router_id": device_ip_2,
        }]

        # configuring bgp global
        for req_body in bgp_request_body:
            self.perform_add_bgp_global(req_body)

        nbr_req = {
            "mgt_ip": device_ip_1,
            "remote_asn": device_2_asn,
            "vrf_name": "default",
            "neighbor_ip": neighbor_ip_1
        }

        # add bgp neighbor config
        response = self.put_req("bgp_nbr", nbr_req)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.get_req("bgp_nbr", nbr_req)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(nbr_req.get("neighbor_ip"), response.json()["neighbor_ip"])
        self.assertEqual(nbr_req.get("remote_asn"), response.json()["remote_asn"])
        self.assertEqual(nbr_req.get("vrf_name"), response.json()["vrf_name"])

        response = self.get_req("bgp_nbr_remote_bgp", {
            "neighbor_ip": neighbor_ip_1, "mgt_ip": device_ip_1,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_body = response.json()
        self.assertTrue(any([i["local_asn"] == device_2_asn for i in response_body]))
        self.assertTrue(any([i["router_id"] == device_ip_2 for i in response_body]))

        # clean up
        response = self.del_req("bgp_nbr", nbr_req)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.get_req("bgp_nbr", nbr_req)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        for req_body in bgp_request_body:
            self.perform_delete_bgp_global(req_body)

    def test_bgp_neighbors_local_bgp(self):
        device_ip_1 = self.device_ips[0]
        device_ip_2 = self.device_ips[1]

        device_1_asn = 64500
        device_2_asn = 64501

        neighbor_ip_1 = "1.1.1.1"

        bgp_request_body = [{
            "mgt_ip": device_ip_1,
            "vrf_name": "default",
            "local_asn": device_1_asn,
            "router_id": device_ip_1,
        }, {
            "mgt_ip": device_ip_2,
            "vrf_name": "default",
            "local_asn": device_2_asn,
            "router_id": device_ip_2,
        }]

        # configuring bgp global
        for req_body in bgp_request_body:
            self.perform_add_bgp_global(req_body)

        nbr_req = {
            "mgt_ip": device_ip_1,
            "remote_asn": 65501,
            "vrf_name": "default",
            "local_asn": device_2_asn,
            "neighbor_ip": neighbor_ip_1
        }

        # add bgp neighbor config
        response = self.put_req("bgp_nbr", nbr_req)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.get_req("bgp_nbr", nbr_req)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(nbr_req.get("neighbor_ip"), response.json()["neighbor_ip"])
        self.assertEqual(nbr_req.get("remote_asn"), response.json()["remote_asn"])
        self.assertEqual(nbr_req.get("vrf_name"), response.json()["vrf_name"])

        response = self.get_req("bgp_nbr_local_bgp", {
            "neighbor_ip": neighbor_ip_1, "mgt_ip": device_ip_1,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_body = response.json()
        self.assertTrue(any([i["local_asn"] == device_2_asn for i in response_body]))
        self.assertTrue(any([i["router_id"] == device_ip_2 for i in response_body]))

        # clean up
        response = self.del_req("bgp_nbr", nbr_req)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.get_req("bgp_nbr", nbr_req)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        for req_body in bgp_request_body:
            self.perform_delete_bgp_global(req_body)
