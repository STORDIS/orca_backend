from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status


class ORCATest(APITestCase):
    device_ips = []
    ether_names = []

    def setUp(self):
        response = self.client.get(reverse("device_list"))
        if not response.json():
            response = self.client.get(reverse("discover"))
            if not response or response.get("result") == "Fail":
                self.fail("Failed to discover devices")

        for device in response.json():
            self.device_ips.append(device["mgt_ip"])

        if self.device_ips:
            response = self.client.get(
                reverse("device_interface_list"), {"mgt_ip": self.device_ips[0]}
            )
            while len(self.ether_names) < 5:
                if (
                    (intfs := response.json())
                    and (ifc := intfs.pop())
                    and ifc["name"].startswith("Ethernet")
                ):
                    self.ether_names.append(ifc["name"])

    def perform_del_port_chnl(self, request_body):
        response = self.client.delete(
            reverse("device_port_chnl"),
            request_body,
            format="json",
        )
        self.assertTrue(
            response.status_code == status.HTTP_200_OK
            or any(
                "resource not found" in res.lower() for res in response.json()["result"]
            )
        )
        for data in request_body if isinstance(request_body, list) else [request_body] if request_body else []:
            response = self.client.get(
                reverse("device_port_chnl"),
                data,
            )
            self.assertIsNone(response.json())
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def perform_add_port_chnl(self, request_body):
        for data in request_body if isinstance(request_body, list) else [request_body] if request_body else []:
            device_ip = data["mgt_ip"]

            response = self.client.get(
                reverse("device_port_chnl"),
                {"mgt_ip": device_ip, "chnl_name": data["chnl_name"]},
            )

            self.assertIsNone(response.json())
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            response = self.client.put(reverse("device_port_chnl"), data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            response = self.client.get(
                reverse("device_port_chnl"),
                {"mgt_ip": device_ip, "chnl_name": data["chnl_name"]},
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.json()["mtu"], data["mtu"])
            self.assertEqual(response.json()["admin_sts"], data["admin_status"])

    def perform_del_add_del_port_chnl(self, request_body):
        self.perform_del_port_chnl(request_body)
        self.perform_add_port_chnl(request_body)
        self.perform_del_port_chnl(request_body)
