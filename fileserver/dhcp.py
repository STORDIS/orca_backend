import datetime
import io
import json
import os
import paramiko

from fileserver import constants
from log_manager.logger import get_backend_logger

_logger = get_backend_logger()


def create_ssh_client(ip, username, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, username=username, password=password)
    return client


def get_dhcp_backup_file(ip, username, password, filename):
    client = create_ssh_client(ip, username, password)
    path = constants.dhcp_path + filename
    with client.open_sftp() as sftp:
        app_directory = os.path.dirname(os.path.abspath(__file__))
        local_file_path = os.path.join(app_directory, 'media', "dhcpd.conf")
        sftp.get(path, local_file_path)
        file = open(local_file_path, "rb+")
        return file


def get_dhcp_backup_files_list(ip, username, password):
    client = create_ssh_client(ip, username, password)
    with client.open_sftp() as sftp:
        return [file for file in sftp.listdir(path=constants.dhcp_path) if file.startswith(constants.dhcp_backup_prefix)]


def get_dhcp_config(ip, username, password):
    client = create_ssh_client(ip, username, password)
    with client.open_sftp() as sftp:
        path = f"{constants.dhcp_path}/dhcpd.conf"
        with sftp.open(path, 'r') as f:
            file = io.BytesIO(f.read())
        return file


def put_dhcp_config(ip, username, password, content):
    client = create_ssh_client(ip, username, password)
    with client.open_sftp() as sftp:
        dhcp_file_path = f"{constants.dhcp_path}/dhcpd.conf"
        backup_files = [
            file for file in sftp.listdir(constants.dhcp_path) if file.startswith(constants.dhcp_backup_prefix)
        ]
        if len(backup_files) > 10:
            backup_files.sort(
                key=lambda x: datetime.datetime.strptime(
                    x.replace(constants.dhcp_backup_prefix, ""), "%Y-%m-%d_%H:%M:%S"
                ),
                reverse=True
            )

            # Remove the oldest backup files
            for file in backup_files[10:]:
                sftp.remove(constants.dhcp_path + file)

        # Create a new backup file
        new_backup_file = f"{constants.dhcp_backup_prefix}{datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}"
        try:
            client.exec_command(
                f"sudo cp {dhcp_file_path} {constants.dhcp_path}{new_backup_file}"
            )
        except FileNotFoundError:
            _logger.debug(f"File {dhcp_file_path} not found")
        except Exception as e:
            _logger.error(e)
            raise
        client.exec_command(f"echo '{json.dumps(content)}' | sudo tee {dhcp_file_path}")
        client.exec_command(f"sudo systemctl restart isc-dhcp-server")
        return {"message": "Config updated successfully"}
