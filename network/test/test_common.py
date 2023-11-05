from rest_framework.test import APITestCase
from django.urls import reverse

class ORCATests(APITestCase):
    def retrieve_device(self):
        """
        Retrieves a device and ethernet from DB.

        :return: A tuple containing the device IP, the first Ethernet interface name,
                 and the second Ethernet interface name.
        """
        response = self.client.get(reverse("device_list"))
        if not response.json():
            response = self.client.get(reverse("discover"))
            if not response or response.get("result") == "Fail":
                self.fail("Failed to discover devices")

        device_ip = response.json()[0]["mgt_ip"]
        response = self.client.get(
            reverse("device_interface_list"), {"mgt_ip": device_ip}
        )
        ether_name = None
        ether_name_2 = None

        for intf in response.json():
            if intf["name"].startswith("Ethernet"):
                if not ether_name:
                    ether_name = intf["name"]
                    continue
                ether_name_2 = intf["name"]
                break

        return (device_ip, ether_name, ether_name_2)