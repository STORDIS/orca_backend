from unittest.mock import patch, MagicMock
from rest_framework import status
from network.test.test_common import TestORCA


class TestSetup(TestORCA):

    def test_image_list(self):
        response = self.get_req("device")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for i in response.json():
            self.assertTrue(len(i["image_list"]) > 0)

    def test_image_install_on_sonic_device(self):

        request_body = {
            "image_url": "http://10.10.128.249/sonic/release/4.4.0/sonic-broadcom-enterprise-advanced.bin",
            "discover_also": True,
            "device_ips": self.sonic_ips
        }

        response = self.put_req("install_image", req_json=request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_body = response.json()
        install_responses = response_body.get("install_response", {})
        response = self.get_req("device")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for device_ip in self.sonic_ips:
            self.assertTrue(install_responses is not None)
            self.assertTrue(install_responses.get(device_ip).get("error") is None)
            self.assertTrue(install_responses.get(device_ip).get("output") is not None)
            for i in response.json():
                if i["device_ip"] == device_ip:
                    self.assertTrue("SONiC-OS-4.4.0-Enterprise_Base" in i["image_list"])

    def test_image_install_on_onie_device(self):
        request_body = {
            "image_url": "http://10.10.128.249/sonic/release/4.4.0/sonic-broadcom-enterprise-advanced.bin",
            "discover_also": True,
            "device_ips": self.onie_ips
        }

        response = self.put_req("install_image", req_json=request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_body = response.json()
        install_responses = response_body.get("install_response", {})
        self.assertTrue(install_responses is not None)
        for device_ip in self.onie_ips:
            self.assertTrue(install_responses.get(device_ip).get("error") is None)
            self.assertTrue(install_responses.get(device_ip).get("output") is not None)
            for i in response.json():
                if i["device_ip"] == device_ip:
                    self.assertTrue("SONiC-OS-4.4.0-Enterprise_Base" in i["image_list"])

    def test_install_image_with_network_ip(self):
        # ip is hardcoded to 10.10.229.123/32 because ony ip with onie install mode running
        # using 32 because it is only gives one ip
        device_ips = [f"{self.onie_ips[0]}/32"]

        req_body = {
            "device_ips": device_ips,
            "image_url": "http://10.10.128.249/sonic/release/4.4.0/sonic-broadcom-enterprise-advanced.bin",
            "discover_also": True
        }

        # when network ip is provided it returns list of networks with device details
        response = self.put_req(
            "install_image", req_json=req_body
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_body = response.json()
        for device_ip in device_ips:
            networks_details = response_body.get("networks", {}).get(device_ip, {})
            for i in networks_details:
                self.assertTrue(i.get("mac_address") is not None)
                self.assertTrue(i.get("version") is not None)
                self.assertTrue(i.get("platform") is not None)

    def test_switch_image(self, ):
        response = self.get_req("device")
        image_list = response.json()[0]["image_list"]
        current_image = response.json()[0]["img_name"]
        new_image = None

        # checking if there are two or more images
        if len(image_list) >= 2:
            for image_name in image_list:
                if current_image != image_name:
                    new_image = image_name
                    break
        else:

            # if there is only one image then install new image and switch
            if current_image == "SONiC-OS-4.4.0-Enterprise_Base":
                url = "http://10.10.128.249/sonic/release/4.2.0/sonic-broadcom-enterprise-advanced.bin"
            else:
                url = "http://10.10.128.249/sonic/release/4.4.0/sonic-broadcom-enterprise-advanced.bin"

            req_body = {
                "image_url": url,
                "discover_also": True,
                "device_ips": self.sonic_ips
            }

            response = self.put_req("install_image", req_json=req_body)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            response_body = response.json()
            install_responses = response_body.get("install_response", {})
            for device_ip in self.sonic_ips:
                self.assertTrue(install_responses.get(device_ip).get("error") is None)
                self.assertTrue(install_responses.get(device_ip).get("output") is not None)

            response = self.get_req("device")
            image_list = response.json()[0]["image_list"]
            self.assertTrue(len(image_list) >= 2)

            for image_name in image_list:
                if current_image != image_name:
                    new_image = image_name
                    break

        # switching image
        response = self.put_req("switch_image", req_json={
            "image_name": new_image,
            "mgt_ip": self.sonic_ips
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.get_req("device")
        self.assertEqual(new_image, response.json()[0]["img_name"])

        # switching back to previous image
        response = self.put_req("switch_image", req_json={
            "image_name": current_image,
            "mgt_ip": self.sonic_ips
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.get_req("device")
        self.assertEqual(current_image, response.json()[0]["img_name"])
