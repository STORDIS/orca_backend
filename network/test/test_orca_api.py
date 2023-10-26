from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status

class InterfaceAPITestCase(APITestCase):
    def test_put_device_interfaces(self):
        response = self.client.get(reverse("device_list"))
        device_ip = response.json()[1]["mgt_ip"]
        response = self.client.get(
        reverse("device_interface_list"), 
        {"mgt_ip": device_ip},
            )
        ether_name = response.json()[0]["name"]


    #  Enabled
        request_body = [{"mgt_ip": device_ip, "name": ether_name, "enabled": False}]
        for data in request_body:
            response = self.client.put(reverse("device_interface_list"), data)
            response = self.client.get(
            reverse("device_interface_list"),
            {"mgt_ip": device_ip, "intfc_name": ether_name},
        )
            print(response.json())
        self.assertEqual(response.json()["enabled"], data["enabled"])

    #    mtu
        request_body = [{"mgt_ip": device_ip, "name": ether_name, "mtu": 9200}]
        for data in request_body:
            response = self.client.put(reverse("device_interface_list"), data)
            response = self.client.get(
            reverse("device_interface_list"),
            {"mgt_ip": device_ip, "intfc_name": ether_name},
        )
        self.assertEqual(response.json()["mtu"], data["mtu"])

    #     #description
        request_body = [{"mgt_ip": device_ip, "name": ether_name, "description": "Sample_Description"}]
        for data in request_body:
            response = self.client.put(reverse("device_interface_list"), data)
            response = self.client.get(
            reverse("device_interface_list"),
            {"mgt_ip": device_ip, "intfc_name": ether_name},
        )
        self.assertEqual(response.json()["description"], data["description"])
        
    #     #port-speed
        request_body = [{"mgt_ip": device_ip, "name": ether_name, "speed": "SPEED_100GB"}]
        for data in request_body:
            response = self.client.put(reverse("device_interface_list"), data)
            response = self.client.get(
            reverse("device_interface_list"),
            {"mgt_ip": device_ip, "intfc_name": ether_name},
        )
        self.assertEqual(response.json()["speed"], data["speed"])

    #   Multiple Interfaces for update

    def test_multiple_interfaces_list(self):
        request_body = [
                    {
                        "mgt_ip": "10.10.130.213",
                        "name": "Ethernet56",
                        "enabled": True,
                        "mtu": "9100",
                        "speed": "SPEED_100GB",
                        "description": "Management"
                    },
                    {
                        "mgt_ip": "10.10.130.213",
                        "name": "Ethernet76",
                        "enabled": True,
                        "mtu": "9100",
                        "speed": "SPEED_40GB",
                        "description": "Mainport"
                    }
                ]

        response = self.client.put(reverse("device_interface_list"), request_body, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"status": "Config Successful"})

class PortchannelsAPITestcase(APITestCase):
    def test_put_device_Portchannel(self):
        response = self.client.get(reverse("device_list"))
        device_ip = response.json()[1]["mgt_ip"]
        response = self.client.get(
        reverse("device_port_chnl"), 
        {"mgt_ip": device_ip},
        )
        name = response.json()[0]["lag_name"]

        # mtu
        request_body = [{"mgt_ip": device_ip, "chnl_name": name, "mtu": 8000}]
        for data in request_body:
            response = self.client.put(reverse("device_port_chnl"), data)
            response = self.client.get(
                reverse("device_port_chnl"),
                {"mgt_ip": device_ip, "chnl_name": name},)
        self.assertEqual(response.json()["mtu"], data["mtu"])

        # Admin status
        request_body = [{"mgt_ip": device_ip, "chnl_name": name, "admin_status": "up"}]
        for data in request_body:
            response = self.client.put(reverse("device_port_chnl"), data)
            response = self.client.get(
                reverse("device_port_chnl"),
                {"mgt_ip": device_ip, "chnl_name": name},)
        self.assertEqual(response.json()["admin_sts"], data["admin_status"])

    #    Multiple Portchannels update request

    def test_multiple_portchanls_list(self):
        request_body = [
                    {
                        "mgt_ip": "10.10.130.213",
                        "chnl_name": "PortChannel103",
                        "mtu": "9100",
                        "admin_status": "down"
                    },
                    {
                        "mgt_ip": "10.10.130.213",
                        "chnl_name": "PortChannel102",
                        "mtu": "9200",
                        "admin_status": "down"
                    }
                ]

        response = self.client.put(reverse("device_port_chnl"), request_body, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"status": "Config Successful"})
