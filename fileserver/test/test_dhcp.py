import datetime
import time

from fileserver import constants
from fileserver.ssh import ssh_client_with_username_password
from fileserver.scheduler import scheduler, add_dhcp_leases_scheduler
from fileserver.test.test_common import TestCommon


class TestDHCP(TestCommon):
    device_ip = "10.10.229.124"
    username = "admin"
    password = "YourPaSsWoRd"
    dhcp_path = "/tmp/"

    def test_dhcp_server_credentials(self):
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

    def test_dhcp_server_config(self):
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

    def test_dhcp_server_backups(self):
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

        file_data["content"] = "new file content"
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

    def test_dhcp_leases_schedular(self):
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
        constants.dhcp_schedule_interval = 60

        # start scheduler
        add_dhcp_leases_scheduler()

        # modify job start time
        job = scheduler.get_job(f"dhcp_list")
        print(job.next_run_time)
        job.modify(
            next_run_time=datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(seconds=5)
        )
        print(job.next_run_time)
        time.sleep(10)
        retries = 10
        while retries > 0:
            if job.next_run_time > datetime.datetime.now(tz=datetime.timezone.utc):
                time.sleep(10)
            else:
                break
            retries -= 1
            print(job.next_run_time)

        # list leases
        response = self.get_req("dhcp_list")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json()) > 0)
        self.assertTrue(all([i.get("hostname").startswith("sonic") for i in response.json()]))

    @classmethod
    def setUpClass(cls):
        cls.device_ip = "10.10.229.124"
        cls.username = "admin"
        cls.password = "YourPaSsWoRd"
        cls.dhcp_path = "/tmp/"
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
        scheduler.shutdown()
