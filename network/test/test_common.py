from rest_framework.test import APITestCase
from django.urls import reverse

class ORCATest(APITestCase):
    
    device_ips=[]
    ether_names=[]
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
                if (intfs:=response.json()) and (ifc:=intfs.pop()) and ifc["name"].startswith("Ethernet"):
                    self.ether_names.append(ifc["name"])
