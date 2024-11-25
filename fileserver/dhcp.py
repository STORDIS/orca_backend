import datetime
from fileserver import constants
from fileserver.models import DHCPServerDetails
from fileserver.ssh import create_ssh_key_based_authentication, ssh_client_with_public_key
from log_manager.logger import get_backend_logger

_logger = get_backend_logger()


def get_dhcp_backup_file(ip, username, filename):
    client = ssh_client_with_public_key(ip, username)
    with client.open_sftp() as sftp:
        return _get_sftp_file_content(sftp, constants.dhcp_path, filename)


def get_dhcp_backup_files_list(ip, username):
    client = ssh_client_with_public_key(ip, username)
    with client.open_sftp() as sftp:
        return [
            _get_sftp_file_content(sftp, path=constants.dhcp_path, filename=file)
            for file in sftp.listdir(path=constants.dhcp_path)
            if file.startswith(constants.dhcp_backup_prefix)
        ]


def _get_sftp_file_content(sftp, path, filename):
    with sftp.open(path + filename, 'r') as f:
        return {"content": f.read(), "filename": filename}


def get_dhcp_config(ip, username):
    client = ssh_client_with_public_key(ip, username)
    with client.open_sftp() as sftp:
        _get_sftp_file_content(sftp, path=constants.dhcp_path, filename="dhcpd.conf")


def put_dhcp_config(ip, username, content):
    client = ssh_client_with_public_key(ip, username)
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
        client.exec_command(f"echo '{content}' | sudo tee {dhcp_file_path}")
        client.exec_command(f"sudo systemctl restart isc-dhcp-server")
        return {"message": "Config updated successfully"}


def update_dhcp_access(ip, username, password):
    try:
        create_ssh_key_based_authentication(ip, username, password)
        DHCPServerDetails.objects.update_or_create(device_ip=ip, defaults={"username": username, "ssh_access": True})
        _logger.info(f"SSH access enabled on {ip}.")
    except Exception as e:
        DHCPServerDetails.objects.update_or_create(device_ip=ip, defaults={"username": username, "ssh_access": False})
        _logger.error(e)
        _logger.error(f"Failed to enable SSH access on {ip}.")
        import traceback
        print(traceback.format_exc())
        raise
