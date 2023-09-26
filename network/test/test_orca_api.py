from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from orca_nw_lib.common import Speed

class TaskAPITestCase(APITestCase):
    def test_get_task_list(self):
        response = self.client.get(reverse("device_list"))
        device_ip = response.json()[0]["mgt_ip"]

        response = self.client.get(
            reverse("device_interface_list"), {"mgt_ip": device_ip}
        )
        ether_name = response.json()[0]["name"]
        print(ether_name)
    
        #Enabled
        request_body = {"mgt_ip": device_ip, "name": ether_name, "enabled": False}
        response = self.client.put(reverse("device_interface_list"), request_body)
        response = self.client.get(
            reverse("device_interface_list"),
            {"mgt_ip": device_ip, "intfc_name": ether_name},
        )
        self.assertEqual(response.json()[0]["enabled"], request_body["enabled"])
        #self.assertEqual(response.status_code, status.HTTP_200_OK)

        # mtu

        request_body = {"mgt_ip": device_ip, "name": ether_name, "mtu": 9200}
        response = self.client.put(reverse("device_interface_list"), request_body)
        response = self.client.get(
            reverse("device_interface_list"),
            {"mgt_ip": device_ip, "intfc_name": ether_name},)
        self.assertEqual(response.json()[0]["mtu"], request_body["mtu"])

        # loopback-mode

        # request_body = {"mgt_ip": device_ip, "name": ether_name, "fec": False}
        # response = self.client.put(reverse("device_interface_list"), request_body)
        # print(response.json())
        # response = self.client.get(
        #     reverse("device_interface_list"),
        #     {"mgt_ip": device_ip, "intfc_name": ether_name},
        # )
        # self.assertEqual(response.json()[0]["fec"], request_body["fec"])
       # self.assertEqual(response.status_code, status.HTTP_200_OK)

        #description

        request_body = {"mgt_ip": device_ip, "name": ether_name, "description": "port"}
        response = self.client.put(reverse("device_interface_list"), request_body)
        response = self.client.get(
            reverse("device_interface_list"),
            {"mgt_ip": device_ip, "intfc_name": ether_name},
        )
        self.assertEqual(response.json()[0]["description"], request_body["description"])
        
        #port-speed
        
        request_body = {"mgt_ip": device_ip, "name": ether_name, "speed": "SPEED_100GB"}
        response = self.client.put(reverse("device_interface_list"), request_body)
        response = self.client.get(
            reverse("device_interface_list"),
            {"mgt_ip": device_ip, "intfc_name": ether_name},
        )
        self.assertEqual(response.json()[0]["speed"], request_body["speed"])