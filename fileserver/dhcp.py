import datetime
import hashlib

from fileserver import constants
from fileserver.models import DHCPServerDetails
from fileserver.ssh import create_ssh_key_based_authentication, ssh_client_with_private_key, \
    is_ssh_key_based_authentication_enabled
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
    client = ssh_client_with_private_key(ip, username)
    with client.open_sftp() as sftp:
        file_content = get_sftp_file_content(sftp, constants.dhcp_path, filename)

    client.close()
    return file_content


def get_dhcp_backup_files_list(ip, username):
    """
    Get the list of backup files from the DHCP server.

    Args:
        ip (str): The IP address of the DHCP server.
        username (str): The username to use for authentication.

    Returns:
        list: A list of dictionaries, each containing the content of a backup file and its name.
    """
    client = ssh_client_with_private_key(ip, username)
    files = []
    sftp = client.open_sftp()
    back_files = list_backup_files(sftp, constants.dhcp_path)
    for f in back_files:
        files.append(get_sftp_file_content(sftp, constants.dhcp_path, f))

    client.close()
    return files


def get_sftp_file_content(sftp, path, filename):
    """
    Get the specified file from the SFTP server.

    Args:
        sftp (paramiko.sftp_client.SFTPClient): An SFTP client object.
        path (str): The path to the file on the SFTP server.
        filename (str): The name of the file to retrieve.
    """
    with sftp.open(f"{path}{filename}", 'r') as f:
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
    client = ssh_client_with_private_key(ip, username)
    with client.open_sftp() as sftp:
        file_content = get_sftp_file_content(sftp, path=constants.dhcp_path, filename="dhcpd.conf")
    client.close()
    return file_content


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
        # Check if SSH access is already enabled
        _logger.info(f"Enabling SSH access on {ip}.")
        if is_ssh_key_based_authentication_enabled(ip, username):
            _logger.info(f"SSH access already enabled on {ip}.")
            _save_dhcp_service_details_to_db(ip, username, ssh_access=True)
        else:
            # Enable SSH access
            create_ssh_key_based_authentication(ip, username, password)
            _save_dhcp_service_details_to_db(ip, username, ssh_access=True)
            _logger.info(f"SSH access enabled on {ip}.")
    except Exception as e:
        _logger.error(e)
        _save_dhcp_service_details_to_db(ip, username, ssh_access=False)
        _logger.error(f"Failed to enable SSH access on {ip}.")
        raise


def _save_dhcp_service_details_to_db(ip, username, ssh_access):
    """
    Save DHCP server details to the database.

    Args:
        ip (str): The IP address of the DHCP server.
        username (str): The username to use for authentication.
        ssh_access (bool): Whether SSH access is enabled.

    Returns:
        None
    """

    # Delete all existing DHCP server details, because we only want one DHCP server.
    DHCPServerDetails.objects.all().delete()

    # Create a new DHCP server details object
    dhcp_server_details = DHCPServerDetails(device_ip=ip, username=username, ssh_access=ssh_access)
    dhcp_server_details.save()

    _logger.info(f"DHCP server details saved to database.")


def delete_dhcp_backup_file(ip, username, file_name: str):
    """
    Delete the specified backup file from the DHCP server.

    Args:
        ip (str): The IP address of the DHCP server.
        username (str): The username to use for authentication.
        file_name (str): The name of the backup file to delete.

    Returns:
        None
    """
    client = ssh_client_with_private_key(ip=ip, username=username)
    stdin, stdout, stderr = client.exec_command(f"sudo rm {constants.dhcp_path}{file_name}")
    output = stdout.read().decode()
    error = stderr.read().decode()
    client.close()
    return output, error


def calculate_checksum(content):
    """
    Calculate the MD5 checksum of the given content after stripping trailing newlines.

    Args:
        content (str): The content to calculate the checksum for.

    Returns:
        str: The MD5 checksum as a hexadecimal string.
    """
    # Strip trailing newlines before calculating the checksum
    return hashlib.md5(content.strip().encode('utf-8')).hexdigest()


def put_dhcp_config(ip, username, content):
    """
    Upload the DHCP configuration file to the DHCP server.

    Args:
        ip (str): The IP address of the DHCP server.
        username (str): The username to use for authentication.
        content (str): The content of the DHCP configuration file.

    Returns:
        None
    """
    client = ssh_client_with_private_key(ip, username)
    sftp = client.open_sftp()
    dhcp_filename = "dhcpd.conf"

    # verify if there are any changes
    try:
        current_file_details = get_sftp_file_content(sftp, path=constants.dhcp_path, filename=dhcp_filename)
        current_content = current_file_details["content"].decode("utf-8")
    except FileNotFoundError:
        current_content = ""

    current_checksum = calculate_checksum(current_content)
    new_checksum = calculate_checksum(content)

    # Check if there are any changes
    if current_checksum == new_checksum:
        _logger.info(f"No changes detected in DHCP configuration.")
        return "", "No changes detected in DHCP configuration."

    _logger.info(f"Updating DHCP configuration on {ip}.")

    try:

        # Backup the old DHCP configuration file before saving the new one
        backup_old_dhcp_config(client, sftp, path=constants.dhcp_path, filename=dhcp_filename)

        # Update the DHCP configuration file
        output, error = update_dhcp_config(
            client=client, path=constants.dhcp_path, filename=dhcp_filename, content=content
        )

        # Restart the DHCP server
        restart_dhcpd(client)

    except Exception as e:
        _logger.error(f"Failed to update DHCP configuration on {ip}: {e}")
        raise

    finally:
        sftp.close()
        client.close()

    return output, error


def restart_dhcpd(client):
    """
    Restart the DHCP server.

    Args:
        client (paramiko.client.SSHClient): An SSH client object.
    Returns:
        None
    """
    _logger.info(f"Restarting DHCP server.")
    stdin, stdout, stderr = client.exec_command("sudo systemctl restart isc-dhcp-server")
    _logger.info(f"DHCP server restarted.")
    _logger.debug("stdout: " + stdout.read().decode())
    _logger.debug("stderr: " + stderr.read().decode())


def update_dhcp_config(client, path, filename, content):
    """
    Update the DHCP configuration file on the DHCP server.

    Args:
        client (paramiko.client.SSHClient): An SSH client object.
        path (str): The path to the DHCP configuration file.
        filename (str): The name of the DHCP configuration file.
        content (str): The content of the DHCP configuration file.

    Returns:
        None
    """
    _logger.info(f"Updating DHCP configuration.")
    stdin, stdout, stderr = client.exec_command(f'sudo tee {path}{filename} <<EOF\n{content}\nEOF')
    output = stdout.read().decode()
    error = stderr.read().decode()
    return output, error


def backup_old_dhcp_config(client, sftp, path, filename):
    """
    Backup the old DHCP configuration file.

    Args:
        client (paramiko.client.SSHClient): An SSH client object.
        sftp (paramiko.SFTPClient): An SFTP client object.
        path (str): The path to the DHCP configuration file.
        filename (str): The name of the DHCP configuration file.

    Returns:
        None
    """
    _logger.info(f"Backing up old DHCP configuration on {client.get_transport().getpeername()}.")
    backup_files = list_backup_files(sftp, path)
    if len(backup_files) > 9:
        _logger.info(f"Deleting oldest backup file on {client.get_transport().getpeername()}.")
        for file in backup_files[9:]:
            stdin, stdout, stderr = client.exec_command(
                f"sudo rm {path}{file}"
            )
            _logger.debug(f"stdout: {stdout.read().decode()}")
            _logger.debug(f"stderr: {stderr.read().decode()}")
    new_backup_filename = f"{constants.dhcp_backup_prefix}{datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}"
    stdin, stdout, stderr = client.exec_command(
        f"sudo cp {path}{filename} {path}{new_backup_filename}"
    )
    _logger.debug(f"stdout: {stdout.read().decode()}")
    _logger.debug(f"stderr: {stderr.read().decode()}")
    _logger.info(f"Old DHCP configuration backed up on {client.get_transport().getpeername()}.")


def list_backup_files(sftp, path):
    """
    List the backup files in the specified path.

    Args:
        sftp (paramiko.SFTPClient): An SFTP client object.
        path (str): The path to the backup files.

    Returns:
        list: A list of backup file names.
    """
    backup_files = [file for file in sftp.listdir(path) if file.startswith(constants.dhcp_backup_prefix)]

    # Sort the backup files by date
    backup_files.sort(
        key=lambda x: datetime.datetime.strptime(
            x.replace(constants.dhcp_backup_prefix, ""), "%Y-%m-%d_%H:%M:%S"
        ),
        reverse=True,
    )
    return backup_files
