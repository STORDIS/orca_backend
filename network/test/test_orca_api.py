from time import sleep
from rest_framework.test import APITestCase
from django.urls import reverse


class TaskAPITestCase(APITestCase):
    def test_get_task_list(self):
        response = self.client.get(reverse("device_list"))
        device_ip = response.json()[0]["mgt_ip"]

        response = self.client.get(
            reverse("device_interface_list"), {"mgt_ip": device_ip}
        )
        ether_name = response.json()[0]["name"]
        request_body = {"mgt_ip": device_ip, "name": ether_name, "enabled": False}
        response = self.client.put(reverse("device_interface_list"), request_body)
        sleep(5)
        response = self.client.get(
            reverse("device_interface_list"),
            {"mgt_ip": device_ip, "intfc_name": ether_name},
        )
        print(response.json()[0]["enabled"])
        self.assertEqual(response.json()[0]["enabled"], request_body["enabled"])

        request_body = {"mgt_ip": device_ip, "name": ether_name, "enabled": False}
        response = self.client.put(reverse("device_interface_list"), request_body)
        sleep(5)
        response = self.client.get(
            reverse("device_interface_list"),
            {"mgt_ip": device_ip, "intfc_name": ether_name},
        )
        self.assertEqual(response.json()[0]["enabled"], request_body["enabled"])
