from unittest.mock import patch, MagicMock
from rest_framework import status
from network.test.test_common import TestORCA


class TestSetup(TestORCA):

    def test_image_list(self):
        response = self.get_req("device")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for i in response.json():
            self.assertTrue(len(i["image_list"]) > 0)

    @patch('paramiko.SSHClient')
    def test_image_install_on_sonic_device(self, mock_ssh_client):
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh

        # Simulate stdout, stderr, and exit status
        mock_stdout = MagicMock()
        mock_stdout.read.return_value = b"command output"

        mock_stderr = MagicMock()
        mock_stderr.read.return_value = b"error output"

        mock_ssh.exec_command.return_value = (MagicMock(), mock_stdout, mock_stderr)

        device_ip = list(self.device_ips.keys())[0]
        request_body = {
            "image_url": "http://10.10.128.249/sonic/release/4.4.0/sonic-broadcom-enterprise-advanced.bin",
            "discover_also": True,
            "device_ips": [device_ip]
        }

        response = self.put_req("install_image", req_json=request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_body = response.json()
        install_responses = response_body.get("install_response", {})
        self.assertTrue(install_responses is not None)
        self.assertTrue(install_responses.get("10.10.229.123").get("error") is not None)
        self.assertTrue(install_responses.get("10.10.229.123").get("output") is not None)

    @patch('paramiko.SSHClient')
    def test_image_install_on_onie_device(self, mock_ssh_client):
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh

        # Simulate stdout, stderr, and exit status
        mock_stdout = MagicMock()
        mock_stdout.read.return_value = b"command output"

        mock_stderr = MagicMock()
        mock_stderr.read.return_value = b"error output"

        mock_ssh.exec_command.return_value = (MagicMock(), mock_stdout, mock_stderr)

        # hardcoded to 10.10.229.123/32 because ony ip with onie install mode running
        request_body = {
            "image_url": "http://10.10.128.249/sonic/release/4.4.0/sonic-broadcom-enterprise-advanced.bin",
            "discover_also": True,
            "device_ips": ["10.10.229.123"]
        }

        response = self.put_req("install_image", req_json=request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_body = response.json()
        print(response_body)
        install_responses = response_body.get("install_response", {})
        self.assertTrue(install_responses is not None)
        self.assertTrue(install_responses.get("10.10.229.123").get("error") is not None)
        self.assertTrue(install_responses.get("10.10.229.123").get("output") is not None)

    def test_install_image_with_network_ip(self):
        # ip is hardcoded to 10.10.229.123/32 because ony ip with onie install mode running
        # using 32 because it is only gives one ip
        device_ips = ["10.10.229.123/32"]

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
        networks_details = response_body.get("networks", {}).get("10.10.229.123/32", {})
        for i in networks_details:
            self.assertTrue(i.get("mac_address") is not None)
            self.assertTrue(i.get("version") is not None)
            self.assertTrue(i.get("platform") is not None)

    @patch('paramiko.SSHClient')
    def test_switch_image(self, mock_ssh_client):
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh

        # Simulate stdout, stderr, and exit status
        mock_stdout = MagicMock()
        mock_stdout.read.return_value = b"command output"

        mock_stderr = MagicMock()
        mock_stderr.read.return_value = b"error output"

        mock_ssh.exec_command.return_value = (MagicMock(), mock_stdout, mock_stderr)

        device_ip = list(self.device_ips.keys())[0]
        response = self.put_req("switch_image", req_json={
            "image_name": "SONiC-OS-4.4.0-Enterprise_Base",
            "mgt_ip": device_ip
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

