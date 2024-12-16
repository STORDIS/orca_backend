import datetime
import os
import time

import yaml
from celery.result import AsyncResult
from rest_framework import status

from fileserver import constants
from fileserver.ssh import ssh_client_with_username_password
from fileserver.test.test_common import TestCommon


class TestDHCP(TestCommon):
    device_ip = "10.10.229.124"
    username = "admin"
    password = "YourPaSsWoRd"
    dhcp_path = "/tmp/"

    def test_adding_dhcp_public_key_to_dhcp_server(self):
        """ Test adding dhcp public key to dhcp server. """
        data = {
            "device_ip": self.device_ip,
            "username": self.username,
            "password": self.password
        }

        # adding dhcp credentials
        response = self.put_req("dhcp_credentials", data)
        self.assertEqual(response.status_code, 200)

        # get dhcp credentials
        response = self.get_req("dhcp_credentials")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("username"), data["username"])
        self.assertEqual(response.json().get("device_ip"), data["device_ip"])
        self.assertTrue(response.json().get("ssh_access"))

        # delete dhcp credentials
        response = self.del_req("dhcp_credentials", {"device_ip": self.device_ip})
        self.assertEqual(response.status_code, 200)

        # get dhcp credentials
        response = self.get_req("dhcp_credentials")
        self.assertEqual(response.status_code, 204)

    def test_update_dhcpd_conf_file_update(self):
        """ Test updating dhcpd.conf file. """
        device_ip = self.device_ip
        credentials = {
            "device_ip": device_ip,
            "username": self.username,
            "password": self.password
        }

        file_data = {
            "device_ip": device_ip,
            "content": "test_dhcp_server_config"
        }

        # change dhcp path for testing.
        constants.dhcp_path = self.dhcp_path

        # adding dhcp credentials
        response = self.put_req("dhcp_credentials", credentials)
        self.assertEqual(response.status_code, 200)

        # validate dhcp credentials
        response = self.get_req("dhcp_credentials")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("username"), credentials["username"])
        self.assertTrue(response.json().get("ssh_access"))

        # adding dhcp config
        response = self.put_req("dhcp_config", file_data)
        self.assertEqual(response.status_code, 200)

        # get dhcp config
        response = self.get_req("dhcp_config", {"device_ip": device_ip})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(file_data["content"] in response.json().get("content"))

        # delete dhcp credentials
        response = self.del_req("dhcp_credentials", {"device_ip": device_ip})
        self.assertEqual(response.status_code, 200)

        # validate dhcp credentials
        response = self.get_req("dhcp_credentials")
        self.assertEqual(response.status_code, 204)

    def test_to_check_create_dhcp_backup_after_updating_dhcpd_conf(self):
        """
        This test will check if dhcp backup is created after updating dhcp config.
        """
        device_ip = self.device_ip
        credentials = {
            "device_ip": device_ip,
            "username": self.username,
            "password": self.password
        }

        file_data = {
            "device_ip": device_ip,
            "content": "test_dhcp_server_backups"
        }

        # change dhcp path for testing.
        constants.dhcp_path = self.dhcp_path

        # adding dhcp credentials
        response = self.put_req("dhcp_credentials", credentials)
        self.assertEqual(response.status_code, 200)

        # validate dhcp credentials
        response = self.get_req("dhcp_credentials", {"device_ip": device_ip})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("username"), credentials["username"])
        self.assertTrue(response.json().get("ssh_access"))

        # adding dhcp config
        response = self.put_req("dhcp_config", file_data)
        self.assertEqual(response.status_code, 200)

        # get dhcp config
        response = self.get_req("dhcp_config", {"device_ip": device_ip})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(file_data["content"] in response.json().get("content"))

        file_data["content"] = "test_dhcp_server_backups 1"
        # adding dhcp config
        response = self.put_req("dhcp_config", file_data)
        self.assertEqual(response.status_code, 200)

        # get dhcp config
        response = self.get_req("dhcp_config", {"device_ip": device_ip})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(file_data["content"] in response.json().get("content"))

        # list backups
        response = self.get_req("dhcp_backups", {"device_ip": device_ip})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json()) > 0)
        self.assertTrue(all([i.get("filename").startswith(constants.dhcp_backup_prefix) for i in response.json()]))

        # delete dhcp credentials
        response = self.del_req("dhcp_credentials", {"device_ip": device_ip})
        self.assertEqual(response.status_code, 200)

        # validate dhcp credentials
        response = self.get_req("dhcp_credentials")
        self.assertEqual(response.status_code, 204)

    def test_to_check_dhcp_leases_file_task(self):
        """
        Test to check that the DHCP leases file is scanned by the scheduler.
        """
        device_ip = self.device_ip
        credentials = {
            "device_ip": device_ip,
            "username": self.username,
            "password": self.password
        }

        # adding dhcp credentials
        response = self.put_req("dhcp_credentials", credentials)
        self.assertEqual(response.status_code, 200)

        # validate dhcp credentials
        response = self.get_req("dhcp_credentials", {"device_ip": device_ip})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("username"), credentials["username"])
        self.assertTrue(response.json().get("ssh_access"))

        # change dhcp path for testing.
        constants.dhcp_leases_path = f"{self.dhcp_path}dhcpd.leases"

        with self.settings(
                CELERY_TASK_ALWAYS_EAGER=True,
                CELERY_TASK_EAGER_PROPAGATES_EXCEPTIONS=True,
                CELERY_TASK_STORE_EAGER_RESULT=True
        ):
            response = self.put_req("dhcp_scan", {"mgt_ip": device_ip})
            self.assertEqual(response.status_code, 200)
            task_id = response.json()["result"][0]["task_id"]
            self.assertIsNotNone(task_id)

            task_status = ""
            max_retry = 10
            while (task_status.lower() == "started") or (task_status.lower() == "pending"):
                response = self.get_req("celery_task", {"task_id": task_id})
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                task_status = response.json()["status"]
                print(f"{task_status=}")
                if max_retry == 0:
                    break
                else:
                    max_retry -= 1
                time.sleep(10)

            response = self.get_req("celery_task", {"task_id": task_id})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.json()["status"].lower(), "success")

            # using async result because celery not storing test results.
            result = AsyncResult(task_id)
            self.assertEqual(result.status, "SUCCESS")
            ips = [f'192.168.1.{i}' for i in range(10)]
            for i in result.result.get("sonic_devices"):
                self.assertIn(i.get("mgt_ip"), ips)


    @classmethod
    def setUpClass(cls):
        cls.load_test_config()
        client = ssh_client_with_username_password(cls.device_ip, cls.username, cls.password)
        content = ""
        for i in range(10):
            content += f"""
lease 192.168.1.{i} {{
  starts 4 2024/11/21 10:00:00;
  ends 4 2024/11/21 16:00:00;
  cltt 4 2024/11/21 10:00:00;
  binding state active;
  hardware ethernet 00:1a:2b:3c:4d:5e;
  client-hostname sonic{i};
}}\n"""
        stdin, stdout, stderr = client.exec_command(
            f'echo "{content}" | sudo tee {cls.dhcp_path}dhcpd.leases'
        )
        output = stdout.read().decode()
        error = stderr.read().decode()
        assert error == ""
        assert output != ""
        client.close()

    @classmethod
    def tearDownClass(cls):
        client = ssh_client_with_username_password(cls.device_ip, cls.username, cls.password)
        client.exec_command(
            f"sudo rm {cls.dhcp_path}dhcpd.leases"
        )
        client.exec_command(
            f"sudo rm {constants.dhcp_backup_prefix}*"
        )
        client.exec_command(
            f"sudo rm {constants.dhcp_path}dhcpd.conf"
        )
        client.close()

    def test_dhcpd_backup_file_rotation(self):
        """
        Test case for backup file rotation.
        This test case checks 10 backup files are created, old ones are deleted.
        """

        device_ip = self.device_ip
        credentials = {
            "device_ip": device_ip,
            "username": self.username,
            "password": self.password
        }

        file_data = {
            "device_ip": device_ip,
            "content": "file content"
        }

        # change dhcp path for testing.
        constants.dhcp_path = self.dhcp_path

        # adding dhcp credentials
        response = self.put_req("dhcp_credentials", credentials)
        self.assertEqual(response.status_code, 200)

        # validate dhcp credentials
        response = self.get_req("dhcp_credentials", {"device_ip": device_ip})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("username"), credentials["username"])
        self.assertTrue(response.json().get("ssh_access"))

        # adding dhcp config
        response = self.put_req("dhcp_config", file_data)
        self.assertEqual(response.status_code, 200)

        # get dhcp config
        response = self.get_req("dhcp_config", {"device_ip": device_ip})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(file_data["content"] in response.json().get("content"))

        # adding config 10 time create 10 backups
        for i in range(10):
            response = self.put_req("dhcp_config", {
                "device_ip": device_ip,
                "content": f"file content {i}"
            })
            self.assertEqual(response.status_code, 200)

        # get backups
        response = self.get_req("dhcp_backups", {"device_ip": device_ip})
        oldest_backup = response.json()[-1]

        self.assertEqual(len(response.json()), 10)

        # adding config again to check if oldest backup is deleted
        response = self.put_req("dhcp_config", {
            "device_ip": device_ip,
            "content": "file content"
        })
        self.assertEqual(response.status_code, 200)

        # get backups
        response = self.get_req("dhcp_backups", {"device_ip": device_ip})
        self.assertEqual(len(response.json()), 10)
        self.assertTrue(oldest_backup["filename"] not in [i["filename"] for i in response.json()])

        # delete dhcp credentials
        response = self.del_req("dhcp_credentials", {"device_ip": device_ip})
        self.assertEqual(response.status_code, 200)

        # validate dhcp credentials
        response = self.get_req("dhcp_credentials")
        self.assertEqual(response.status_code, 204)

    def test_dhcpd_conf_checksum_exists(self):
        """
        Test to validate dhcpd.conf checksum exists
        """
        device_ip = self.device_ip
        credentials = {
            "device_ip": device_ip,
            "username": self.username,
            "password": self.password
        }

        file_data = {
            "device_ip": device_ip,
            "content": "test_dhcp_check_sum"
        }

        # change dhcp path for testing.
        constants.dhcp_path = self.dhcp_path

        # adding dhcp credentials
        response = self.put_req("dhcp_credentials", credentials)
        self.assertEqual(response.status_code, 200)

        # validate dhcp credentials
        response = self.get_req("dhcp_credentials", {"device_ip": device_ip})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("username"), credentials["username"])
        self.assertTrue(response.json().get("ssh_access"))

        # adding dhcp config
        response = self.put_req("dhcp_config", file_data)
        self.assertEqual(response.status_code, 200)

        # get dhcp config
        response = self.get_req("dhcp_config", {"device_ip": device_ip})
        self.assertEqual(response.status_code, 200)

        # adding same content to check if checksum is same
        response = self.put_req("dhcp_config", file_data)
        self.assertEqual(response.status_code, 500)
        response_body = response.json()
        self.assertTrue(
            response_body.get("result")[0]["message"].lower(),
            "No changes detected in DHCP configuration.".lower()
        )

        # delete dhcp credentials
        response = self.del_req("dhcp_credentials", {"device_ip": device_ip})
        self.assertEqual(response.status_code, 200)

        # validate dhcp credentials
        response = self.get_req("dhcp_credentials")
        self.assertEqual(response.status_code, 204)

    @classmethod
    def load_test_config(cls):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        config_file_path = os.path.join(dir_path, 'test_dhcp_config.yaml')
        with open(config_file_path, "r") as stream:
            try:
                config = yaml.safe_load(stream)
                cls.device_ip = config["device_ip"]
                cls.username = config["username"]
                cls.password = config["password"]
                cls.dhcp_path = config.get("test_folder", "/tmp/")
            except yaml.YAMLError as exc:
                print(exc)

    def test_dhcp_with_invalid_ip(self):
        device_ip = "lasmxasmxs"  # invalid ip
        credentials = {
            "device_ip": device_ip,
            "username": self.username,
            "password": self.password
        }
        response = self.put_req("dhcp_credentials", credentials)
        self.assertEqual(response.status_code, 400)

    def test_dhcp_access_already_exists(self):
        device_ip = self.device_ip
        credentials = {
            "device_ip": device_ip,
            "username": self.username,
            "password": self.password
        }
        response = self.put_req("dhcp_credentials", credentials)
        self.assertEqual(response.status_code, 200)

        response = self.get_req("dhcp_credentials", {"device_ip": device_ip})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("username"), credentials["username"])
        self.assertTrue(response.json().get("ssh_access"))

        # checking ssh access with dummy ip
        credentials["device_ip"] = "127.0.0.1"
        response = self.put_req("dhcp_credentials", credentials)
        self.assertEqual(response.status_code, 500)  # failed to add credentials but saved ip to db

        response = self.get_req("dhcp_credentials", {"device_ip": device_ip})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("username"), credentials["username"])
        self.assertFalse(response.json().get("ssh_access"))

        # switching back to valid ip using only username
        credentials = {
            "device_ip": device_ip,
            "username": self.username
        }
        response = self.put_req("dhcp_credentials", credentials)
        self.assertEqual(response.status_code, 200)

        response = self.get_req("dhcp_credentials", {"device_ip": device_ip})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("username"), credentials["username"])
        self.assertTrue(response.json().get("ssh_access"))

        # delete dhcp credentials
        response = self.del_req("dhcp_credentials", {"device_ip": device_ip})
        self.assertEqual(response.status_code, 200)

        response = self.get_req("dhcp_credentials", {"device_ip": device_ip})
        self.assertEqual(response.status_code, 204)
