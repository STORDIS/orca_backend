import datetime
import json
import os

import paramiko
from django.http import FileResponse
from rest_framework import status
from rest_framework.response import Response

from log_manager.logger import get_backend_logger

_logger = get_backend_logger()


def create_ssh_client(ip, username, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, username=username, password=password)
    return client


def get_dhcp_backup_file(ip, username, password, filename):
    client = create_ssh_client(ip, username, password)
    path = "/etc/dhcp/" + filename
    with client.open_sftp() as sftp:
        app_directory = os.path.dirname(os.path.abspath(__file__))
        local_file_path = os.path.join(app_directory, 'media', "dhcpd.conf")
        sftp.get(path, local_file_path)
        file = open(local_file_path, "rb+")
        return file


def get_dhcp_backup_files_list(ip, username, password):
    client = create_ssh_client(ip, username, password)
    path = "/etc/dhcp/"
    with client.open_sftp() as sftp:
        return [file for file in sftp.listdir(path=path) if file.startswith("dhcpd.conf.orca.")]


def get_dhcp_config(ip, username, password):
    client = create_ssh_client(ip, username, password)
    with client.open_sftp() as sftp:
        path = "/etc/dhcp/dhcpd.conf"
        app_directory = os.path.dirname(os.path.abspath(__file__))
        local_file_path = os.path.join(app_directory, 'media', "dhcpd.conf")
        sftp.get(path, local_file_path)
        file = open(local_file_path, "rb+")
        return file


def put_dhcp_config(ip, username, password, content):
    client = create_ssh_client(ip, username, password)
    with client.open_sftp() as sftp:
        path = "/etc/dhcp/"
        dhcp_file_path = "{}/dhcpd.conf".format(path)
        backup_files = [file for file in sftp.listdir(path) if file.startswith("dhcpd.conf.orca.")]
        if len(backup_files) > 10:
            backup_files.sort(
                key=lambda x: datetime.datetime.strptime(
                    x.replace("dhcpd.conf.orca.", ""), "%Y-%m-%d_%H:%M:%S"
                ),
                reverse=True
            )

            # Remove the oldest backup files
            for file in backup_files[10:]:
                sftp.remove(path + file)

        # Create a new backup file
        new_backup_file = f"dhcpd.conf.orca.{datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}"
        try:
            client.exec_command(
                f"sudo cp {dhcp_file_path} {path}{new_backup_file}"
            )
        except FileNotFoundError:
            _logger.debug(f"File {dhcp_file_path} not found")
        except Exception as e:
            _logger.error(e)
            raise
        client.exec_command(f"echo '{json.dumps(content)}' | sudo tee {dhcp_file_path}")
        return {"message": "Config updated successfully"}
