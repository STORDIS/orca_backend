import time
from unittest.mock import patch, MagicMock

import yaml
from rest_framework import status
from network.test.test_common import TestORCA


class TestSetup(TestORCA):
    sonic_ips = []
    onie_ips = []
    sonic_img_details = {}

    def setUp(self):
        super().setUp()
        self.load_test_config()

    def test_image_list(self):
        response = self.get_req("device")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for i in response.json():
            self.assertTrue(len(i["image_list"]) > 0)

    def test_image_install_on_sonic_device(self):

        device_ip = self.sonic_ips[0]
        img_url = self.sonic_img_details.get("url")
        request_body = {
            "image_url": img_url,
            "discover_also": True,
            "device_ips": [device_ip]
        }
        device = self.get_req("device", {"mgt_ip": device_ip})
        current_image = device.json()["img_name"]
        next_img = self.sonic_img_details.get("name")

        response = self.put_req("install_image", req_json=request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_body = response.json()
        install_responses = response_body.get("install_response", {})
        self.assertTrue(install_responses is not None)
        self.assertTrue(install_responses.get(device_ip).get("output") is not None)

        response = self.get_req("device", {"mgt_ip": device_ip})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(next_img, response.json()["img_name"])

        # testing switch image
        # roll back to previous image
        response = self.put_req("switch_image", req_json={
            "image_name": current_image,
            "mgt_ip": device_ip
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.put_req("discover", {"address": device_ip, })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.get_req("device", {"mgt_ip": device_ip})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(current_image in response.json()["img_name"])

    def test_image_install_on_onie_device(self):
        device_ip = self.onie_ips[0]
        request_body = {
            "image_url": self.sonic_img_details.get("url"),
            "discover_also": True,
            "device_ips": [device_ip]
        }

        response = self.put_req("install_image", req_json=request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_body = response.json()
        install_responses = response_body.get("install_response", {})
        self.assertTrue(install_responses is not None)
        self.assertTrue(install_responses.get(device_ip).get("output") is not None)
        # onie changes device ip after installing image.
        # so we cannot test discover on onie device.
        # we need to change device back to onie after install else test will fail.

    def test_install_image_with_network_ip(self):
        # ip is hardcoded to 10.10.229.123/32 because ony ip with onie install mode running
        # using 32 because it is only gives one ip
        device_ips = [f"{self.onie_ips[0]}/32"]

        req_body = {
            "device_ips": device_ips,
            "image_url": self.sonic_img_details.get("url"),
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

    def load_test_config(self):
        file = "./network/test/test_orca_setup_config.yaml"
        with open(file, "r") as stream:
            try:
                config = yaml.safe_load(stream)
                self.sonic_ips = config["sonic_ips"]
                self.onie_ips = config["onie_ips"]
                self.sonic_img_details = config["sonic_img_details"]
            except yaml.YAMLError as exc:
                print(exc)
