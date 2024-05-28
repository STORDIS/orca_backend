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
            )
        )

        response = self.del_req("bgp_global", request_body)
        self.assertTrue(
            response.status_code == status.HTTP_200_OK
            or any(
                "resource not found" in res.get("message", "").lower() for res in response.json()["result"]
            )
        )
        response = self.get_req("bgp_global", request_body)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(response.data)
