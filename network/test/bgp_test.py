"""
This module contains tests for the BGP API.
"""

from rest_framework import status

from network.test.test_common import ORCATest


class BGPTest(ORCATest):
    def test_bgp_global_config(self):
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
                "resource not found" in res.lower() for res in response.json()["result"]
            )
        )
        response = self.get_req("bgp_global", request_body)
        self.assertFalse(response.json())

        response = self.put_req("bgp_global", request_body)
        response = self.get_req("bgp_global", request_body)
        self.assertEqual(request_body.get("local_asn"), response.json()["local_asn"])
        self.assertEqual(request_body.get("vrf_name"), response.json()["vrf_name"])
        self.assertEqual(request_body.get("router_id"), response.json()["router_id"])

        response = self.del_req("bgp_global", request_body)
        self.assertTrue(
            response.status_code == status.HTTP_200_OK
            or any(
                "resource not found" in res.lower() for res in response.json()["result"]
            )
        )
        response = self.get_req("bgp_global", request_body)
        self.assertFalse(response.json())

    def test_bgp_nbr_config(self):
        device_ip = self.device_ips[0]
        request_body = {
            "mgt_ip": device_ip,
            "vrf_name": "default",
            "local_asn": 65000,
            "router_id": device_ip,
        }

        response = self.del_req("bgp_global", request_body)
        self.assertTrue(
            response.status_code == status.HTTP_200_OK
            or any(
                "resource not found" in res.lower() for res in response.json()["result"]
            )
        )
        response = self.get_req("bgp_global", request_body)
        self.assertFalse(response.json())

        response = self.put_req("bgp_global", request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.get_req("bgp_global", request_body)
        self.assertEqual(request_body.get("local_asn"), response.json()["local_asn"])
        self.assertEqual(request_body.get("vrf_name"), response.json()["vrf_name"])
        self.assertEqual(request_body.get("router_id"), response.json()["router_id"])

        # Add a neighbor

        nbr_req = {
            "mgt_ip": device_ip,
            "remote_vrf": "default",
            "local_asn": 65000,
            "remote_asn": 65001,
            "neighbor_ip": "1.1.1.0",
        }

        response = self.del_req("bgp_nbr", nbr_req)
        self.assertTrue(
            response.status_code == status.HTTP_200_OK
            or any(
                "resource not found" in res.lower() for res in response.json()["result"]
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
                "resource not found" in res.lower() for res in response.json()["result"]
            )
        )

        response = self.del_req("bgp_global", request_body)
        self.assertTrue(
            response.status_code == status.HTTP_200_OK
            or any(
                "resource not found" in res.lower() for res in response.json()["result"]
            )
        )
        response = self.get_req("bgp_global", request_body)
        self.assertFalse(response.json())
