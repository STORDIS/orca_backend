import time

import yaml
from celery.result import AsyncResult
from rest_framework import status
from orca_setup.test.test_common import TestCommon


class TestSetup(TestCommon):
    databases = ["default"]
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
            "install_also": True,
            "device_ips": [device_ip]
        }

        # discovering device before installation
        response = self.put_req("discover", {"address": device_ip})
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        device = self.get_req("device", {"mgt_ip": device_ip})
        current_image = device.json()["img_name"]
        next_img = self.sonic_img_details.get("name")

        # installing image
        response = self.put_req("install_image", req_json=request_body)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        response_body = response.json()
        install_task_id = response_body["result"][0]["task_id"]
        self.assertIsNotNone(install_task_id)

        task_status = ""
        max_retry = 30
        while task_status.lower() == "started":
            response = self.get_req("celery_task", {"task_id": install_task_id})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            task_status = response.json()["status"]
            if max_retry == 0:
                break
            else:
                max_retry -= 1
            time.sleep(60)

        response = self.get_req("celery_task", {"task_id": install_task_id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["status"].lower(), "success")

        response = self.get_req("device", {"mgt_ip": device_ip})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(next_img, response.json()["img_name"])

        # testing switch image
        # roll back to previous image
        response = self.put_req("switch_image", req_json={
            "image_name": current_image,
            "mgt_ip": device_ip
        })
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        response_body = response.json()
        task_id = response_body["result"][0]["task_id"]
        self.assertIsNotNone(task_id)

        task_status = ""
        max_retry = 30
        while (task_status.lower() == "started") or (task_status.lower() == "pending"):
            response = self.get_req("celery_task", {"task_id": task_id})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            task_status = response.json()["status"]
            if max_retry == 0:
                break
            else:
                max_retry -= 1
            time.sleep(60)

        response = self.get_req("celery_task", {"task_id": task_id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["status"].lower(), "success")

        response = self.get_req("device", {"mgt_ip": device_ip})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(current_image in response.json()["img_name"])

    def test_image_install_on_onie_device(self):
        device_ip = self.onie_ips[0]
        request_body = {
            "image_url": self.sonic_img_details.get("url"),
            "discover_also": True,
            "install_also": True,
            "device_ips": [device_ip]
        }

        response = self.put_req("install_image", req_json=request_body)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        response_body = response.json()
        result = response_body["result"][0]
        install_task_id = result["task_id"]
        self.assertIsNotNone(install_task_id)

        task_status = ""
        max_retry = 30
        while task_status.lower() == "started":
            response = self.get_req("celery_task", {"task_id": install_task_id})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            task_status = response.json()["status"]
            if max_retry == 0:
                break
            else:
                max_retry -= 1
            time.sleep(60)

        response = self.get_req("celery_task", {"task_id": install_task_id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["status"].lower(), "success")
        # onie changes device ip after installing image.
        # so we cannot test discover on onie device.
        # we need to change device back to onie after install else test will fail.

    def test_network_scan(self):
        sonic_ips_to_scan = [f"{self.sonic_ips[0]}/30"]
        onie_ips_to_scan = [f"{self.onie_ips[0]}/30"]

        req_body = {
            "device_ips": [*sonic_ips_to_scan, *onie_ips_to_scan],
            "image_url": self.sonic_img_details.get("url"),
            "discover_also": True
        }

        # when network ip is provided it returns list of networks with device details
        response = self.put_req(
            "install_image", req_json=req_body
        )
        response_body = response.json()
        results = response_body["result"][0]
        scan_task_id = results.get("scan_task_id", None)
        self.assertIsNotNone(scan_task_id)

        task_status = ""
        max_retry = 30
        while task_status.lower() == "started":
            response = self.get_req("celery_task", {"task_id": scan_task_id})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            task_status = response.json()["status"]
            if max_retry == 0:
                break
            else:
                max_retry -= 1
            time.sleep(60)

        response = self.get_req("celery_task", {"task_id": scan_task_id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # using async result because celery not storing test results.
        result = AsyncResult(scan_task_id)
        self.assertEqual(result.status, "SUCCESS")

        for ip in sonic_ips_to_scan:
            sonic_device = result.result.get("sonic_devices").get(ip)
            self.assertTrue(len(sonic_device) > 0)

        # This condition might fail when device is not in onie mode.
        for ip in onie_ips_to_scan:
            onie_device = result.result.get("onie_devices").get(ip)
            self.assertTrue(len(onie_device) > 0)

    def load_test_config(self):
        file = "./orca_setup/test/test_orca_setup_config.yaml"
        with open(file, "r") as stream:
            try:
                config = yaml.safe_load(stream)
                self.sonic_ips = config["sonic_device_ips"]
                self.onie_ips = config["onie_device_ips"]
                self.sonic_img_details = config["sonic_img_details"]
            except yaml.YAMLError as exc:
                print(exc)
