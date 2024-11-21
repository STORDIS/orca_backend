import time

from fileserver import constants
from fileserver.dhcp import create_ssh_client
from fileserver.scheduler import scheduler, add_dhcp_leases_scheduler
from fileserver.test.test_common import TestCommon


class TestDHCP(TestCommon):
    device_ip = "10.10.229.124"
    username = "admin"
    password = "YourPaSsWoRd"
    dhcp_path = "/tmp/"

    def test_dhcp_server_credentials(self):
        data = {
            "mgt_ip": self.device_ip,
            "username": self.username,
            "password": self.password
        }

        # adding dhcp credentials
        response = self.put_req("dhcp_credentials", data)
        self.assertEqual(response.status_code, 200)

        # get dhcp credentials
        response = self.get_req("dhcp_credentials", {"mgt_ip": self.device_ip})
        print(response.json())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("username"), data["username"])
        self.assertEqual(response.json().get("password"), data["password"])
        self.assertEqual(response.json().get("device_ip"), data["mgt_ip"])

        # delete dhcp credentials
        response = self.del_req("dhcp_credentials", {"mgt_ip": self.device_ip})
        self.assertEqual(response.status_code, 200)

        # get dhcp credentials
        response = self.get_req("dhcp_credentials", {"mgt_ip": self.device_ip})
        self.assertEqual(response.status_code, 204)

    def test_dhcp_server_config(self):
        device_ip = self.device_ip
        credentials = {
            "mgt_ip": device_ip,
            "username": self.username,
            "password": self.password
        }

        file_data = {
            "mgt_ip": device_ip,
            "content": "file content"
        }

        # change dhcp path for testing.
        constants.dhcp_path = self.dhcp_path

        # adding dhcp credentials
        response = self.put_req("dhcp_credentials", credentials)
        self.assertEqual(response.status_code, 200)

        # validate dhcp credentials
        response = self.get_req("dhcp_credentials", {"mgt_ip": device_ip})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("username"), credentials["username"])
        self.assertEqual(response.json().get("password"), credentials["password"])

        # adding dhcp config
        response = self.put_req("dhcp_config", file_data)
        self.assertEqual(response.status_code, 200)

        # get dhcp config
        response = self.get_req("dhcp_config", {"mgt_ip": device_ip})
        self.assertIn(file_data["content"], b"".join(response.streaming_content).decode("utf-8"))

        # delete dhcp credentials
        response = self.del_req("dhcp_credentials", {"mgt_ip": device_ip})
        self.assertEqual(response.status_code, 200)

        # validate dhcp credentials
        response = self.get_req("dhcp_credentials", {"mgt_ip": device_ip})
        self.assertEqual(response.status_code, 204)

    def test_dhcp_server_backups(self):
        device_ip = self.device_ip
        credentials = {
            "mgt_ip": device_ip,
            "username": self.username,
            "password": self.password
        }

        file_data = {
            "mgt_ip": device_ip,
            "content": "file content"
        }

        # change dhcp path for testing.
        constants.dhcp_path = self.dhcp_path

        # adding dhcp credentials
        response = self.put_req("dhcp_credentials", credentials)
        self.assertEqual(response.status_code, 200)

        # validate dhcp credentials
        response = self.get_req("dhcp_credentials", {"mgt_ip": device_ip})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("username"), credentials["username"])
        self.assertEqual(response.json().get("password"), credentials["password"])

        # adding dhcp config
        response = self.put_req("dhcp_config", file_data)
        self.assertEqual(response.status_code, 200)

        # get dhcp config
        response = self.get_req("dhcp_config", {"mgt_ip": device_ip})
        self.assertIn(file_data["content"], b"".join(response.streaming_content).decode("utf-8"))

        # list backups
        response = self.get_req("dhcp_backups", {"mgt_ip": device_ip})
        self.assertEqual(response.status_code, 200)
        print(response.json())
        self.assertTrue(len(response.json()) > 0)
        back_up_file = response.json()[0]

        # get backup
        response = self.get_req("dhcp_backups", {"mgt_ip": device_ip, "filename": back_up_file})
        self.assertEqual(response.status_code, 200)
        self.assertIn(file_data["content"], b"".join(response.streaming_content).decode("utf-8"))

        # delete dhcp credentials
        response = self.del_req("dhcp_credentials", {"mgt_ip": device_ip})
        self.assertEqual(response.status_code, 200)

        # validate dhcp credentials
        response = self.get_req("dhcp_credentials", {"mgt_ip": device_ip})
        self.assertEqual(response.status_code, 204)

    def test_dhcp_leases_schedular(self):
        device_ip = self.device_ip
        credentials = {
            "mgt_ip": device_ip,
            "username": self.username,
            "password": self.password
        }

        # adding dhcp credentials
        response = self.put_req("dhcp_credentials", credentials)
        self.assertEqual(response.status_code, 200)

        # validate dhcp credentials
        response = self.get_req("dhcp_credentials", {"mgt_ip": device_ip})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("username"), credentials["username"])
        self.assertEqual(response.json().get("password"), credentials["password"])

        # change dhcp path for testing.
        constants.dhcp_leases_path = self.dhcp_path
        constants.dhcp_schedule_interval = 5

        # start scheduler
        add_dhcp_leases_scheduler()

        # modify job start time
        job = scheduler.get_job(f"dhcp_list")
        time.sleep(5)
        retries = 5
        while retries > 0:
            if job.next_run_time is None:
                time.sleep(10)
            else:
                break
            retries -= 5
            print(job.next_run_time)
            print(job.is_running())

        # list leases
        response = self.get_req("dhcp_list")
        self.assertEqual(response.status_code, 200)
        print(response.json())
        self.assertTrue(len(response.json()) > 0)
        assert False

    @classmethod
    def setUpClass(cls):
        cls.device_ip = "10.10.229.124"
        cls.username = "admin"
        cls.password = "YourPaSsWoRd"
        cls.dhcp_path = "/tmp/"
        client = create_ssh_client(cls.device_ip, cls.username, cls.password)
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
            }}\n
            """
        client.exec_command(
            f"echo '{content}' | sudo tee {cls.dhcp_path}dhcpd.leases"
        )

    @classmethod
    def tearDownClass(cls):
        client = create_ssh_client(cls.device_ip, cls.username, cls.password)
        client.exec_command(
            f"sudo rm {cls.dhcp_path}dhcpd.leases"
        )
        scheduler.shutdown(wait=False)
