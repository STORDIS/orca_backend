import datetime
from fileserver import constants
from fileserver.models import DHCPServerDetails
from fileserver.ssh import create_ssh_key_based_authentication, ssh_client_with_public_key
from log_manager.logger import get_backend_logger

_logger = get_backend_logger()


def get_dhcp_backup_file(ip, username, filename):
    """
    Get the specified backup file from the DHCP server.

    Args:
        ip (str): The IP address of the DHCP server.
        username (str): The username to use for authentication.
        filename (str): The name of the backup file to retrieve.

    Returns:
        dict: A dictionary containing the content of the backup file and its name.
    """
    client = ssh_client_with_public_key(ip, username)
    with client.open_sftp() as sftp:
        return _get_sftp_file_content(sftp, constants.dhcp_path, filename)


def get_dhcp_backup_files_list(ip, username):
    """
    Get the list of backup files from the DHCP server.

    Args:
        ip (str): The IP address of the DHCP server.
        username (str): The username to use for authentication.

    Returns:
        list: A list of dictionaries, each containing the content of a backup file and its name.
    """
    client = ssh_client_with_public_key(ip, username)
    with client.open_sftp() as sftp:
        return [
            _get_sftp_file_content(sftp, path=constants.dhcp_path, filename=file)
            for file in sftp.listdir(path=constants.dhcp_path)
            if file.startswith(constants.dhcp_backup_prefix)
        ]


def _get_sftp_file_content(sftp, path, filename):
    """
    Get the specified file from the SFTP server.

    Args:
        sftp (paramiko.sftp_client.SFTPClient): An SFTP client object.
        path (str): The path to the file on the SFTP server.
        filename (str): The name of the file to retrieve.
    """
    with sftp.open(path + filename, 'r') as f:
        return {"content": f.read(), "filename": filename}


def get_dhcp_config(ip, username):
    """
    Get the DHCP configuration file from the DHCP server.

    Args:
        ip (str): The IP address of the DHCP server.
        username (str): The username to use for authentication.

    Returns:
        dict: A dictionary containing the content of the DHCP configuration file.
    """
    client = ssh_client_with_public_key(ip, username)
    with client.open_sftp() as sftp:
        _get_sftp_file_content(sftp, path=constants.dhcp_path, filename="dhcpd.conf")


def put_dhcp_config(ip, username, content):
    """
    Update the DHCP configuration file on the DHCP server.

    Args:
        ip (str): The IP address of the DHCP server.
        username (str): The username to use for authentication.
        content (str): The new content of the DHCP configuration file.

    Returns:
        None
    """
    _logger.info(f"Updating DHCP configuration on {ip}")
    client = ssh_client_with_public_key(ip, username)
    with client.open_sftp() as sftp:
        dhcp_file_path = f"{constants.dhcp_path}/dhcpd.conf"
        backup_files = [
            file for file in sftp.listdir(constants.dhcp_path) if file.startswith(constants.dhcp_backup_prefix)
        ]
        if len(backup_files) > 10:
            _logger.info("Removing old DHCP backup files")
            backup_files.sort(
                key=lambda x: datetime.datetime.strptime(
                    x.replace(constants.dhcp_backup_prefix, ""), "%Y-%m-%d_%H:%M:%S"
                ),
                reverse=True
            )

            # Remove the oldest backup files
            for file in backup_files[10:]:
                _logger.info(f"Removing {file}")
                sftp.remove(constants.dhcp_path + file)

        _logger.info(f"Backing up {dhcp_file_path} to {constants.dhcp_path}")
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
        _logger.info(f"Updating {dhcp_file_path}")
        client.exec_command(f"echo '{content}' | sudo tee {dhcp_file_path}")
        client.exec_command(f"sudo systemctl restart isc-dhcp-server")
        return {"message": "Config updated successfully"}


def update_dhcp_access(ip, username, password):
    """
    Enable SSH access on the DHCP server.

    Args:
        ip (str): The IP address of the DHCP server.
        username (str): The username to use for authentication.
        password (str): The password to use for authentication.

    Returns:
        None
    """
    try:
        _logger.info(f"Enabling SSH access on {ip}.")
        create_ssh_key_based_authentication(ip, username, password)
        DHCPServerDetails.objects.update_or_create(device_ip=ip, defaults={"username": username, "ssh_access": True})
        _logger.info(f"SSH access enabled on {ip}.")
    except Exception as e:
        DHCPServerDetails.objects.update_or_create(device_ip=ip, defaults={"username": username, "ssh_access": False})
        _logger.error(e)
        _logger.error(f"Failed to enable SSH access on {ip}.")
        raise
