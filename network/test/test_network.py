from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model


User = get_user_model()


class NetworkTestCases(APITestCase):
    # def test_discovery(self):
    #     response = self.client.get(reverse("discover"))
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    # def test_devices(self):
    #     response = self.client.get(reverse("device_list"))
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_devices(self):
        response = self.client.get(reverse("device"),{"mgt_ip=": "10.10.130.12"})
        #print(response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        