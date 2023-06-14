from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model


User = get_user_model()


class NetworkTestCases(APITestCase):
    # def test_discovery(self):
    #     response = self.client.get(reverse("discover"))
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    dut_ip='10.10.131.111'
    def test_devices(self):
        response = self.client.get(reverse("device"),{"mgt_ip=": self.dut_ip})
        self.assertIsNotNone(response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_port_chnl_config(self):
        
        response = self.client.put(reverse("device_port_chnl"),{"mgt_ip": self.dut_ip,
                                                                "admin_status":"up",
                                                                "chnl_name":"PortChannel101",
                                                                "mtu":9100})
        print(response.json())