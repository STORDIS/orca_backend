import os

import paramiko

from fileserver import constants
from log_manager.logger import get_backend_logger

_logger = get_backend_logger()


def ssh_client_with_username_password(ip, username, password):
    """
    Create an SSH client using the username and password.

    Args:
        ip (str): The IP address of the remote server.
        username (str): The username to use for authentication.
        password (str): The password to use for authentication.

    Returns:
        paramiko.client.SSHClient: An SSH client object.
    """
    # Create an SSH client using the username and password
    _logger.info(f"Connecting to {ip} with username: {username}")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, username=username, password=password)
    _logger.info(f"Connected to {ip} with username: {username}")
    return client


def ssh_copy_id(ip, username, password, public_key):
    """
    Add the public key to the authorized_keys file on the remote server.
    If the public key is already in the authorized_keys file, do nothing.

    Args:
        ip (str): The IP address of the remote server.
        username (str): The username to use for authentication.
        password (str): The password to use for authentication.
        public_key (str): The public key to add to the authorized_keys file.

    Returns:
        None
    """
    _logger.info(f"Adding public key to authorized_keys on {ip}.")
    client = ssh_client_with_username_password(ip, username, password)
    try:
        # Check if the remote .ssh directory exists, and create it if not
        client.exec_command('mkdir -p ~/.ssh')

        # Get the remote authorized_keys file path
        authorized_keys_path = '~/.ssh/authorized_keys'

        # Get the current authorized_keys content
        stdin, stdout, stderr = client.exec_command(f'cat {authorized_keys_path}')
        existing_keys = stdout.read().decode().strip()

        # If the public key is not already in authorized_keys, add it
        if public_key not in existing_keys:
            client.exec_command(f'echo "{public_key}" >> {authorized_keys_path}')
            _logger.info(f"Added public key to authorized_keys on {ip}.")
        else:
            _logger.info(f"Public key already exists in authorized_keys on {ip}.")
    except Exception as e:
        _logger.error(f"Failed to add public key to authorized_keys on {ip}: {e}")
    finally:
        # Close the SSH connection
        client.close()


def ssh_client_with_private_key(ip, username):
    """
    Create an SSH client using the private key.

    Args:
        ip (str): The IP address of the device.
        username (str): The username to use for SSH authentication.

    Returns:
        None
    """
    _logger.info(f"Connecting to {ip} with public key.")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    local_public_key_path = os.path.expanduser(f"{constants.ssh_key_path}/id_rsa")
    client.connect(ip, username=username, key_filename=local_public_key_path)
    return client


def create_ssh_key_based_authentication(ip, username, password):
    """
    Create SSH key-based authentication on the specified device.

    Args:
        ip (str): The IP address of the device.
        username (str): The username to use for SSH authentication.
        password (str): The password to use for SSH authentication.

    Returns:
        None
    """
    public_key_path = os.path.expanduser(f"{constants.ssh_key_path}/id_rsa.pub")
    if not os.path.isfile(public_key_path):
        os.makedirs(os.path.expanduser(constants.ssh_key_path), exist_ok=True)
        generate_ssh_key_pair()

    with open(public_key_path, 'r') as f:
        public_key = f.read()
    _logger.info(f"copying public key to {ip}.")
    # Add the public key to authorized_keys
    ssh_copy_id(ip=ip, username=username, password=password, public_key=public_key)


def generate_ssh_key_pair(key_name="id_rsa", passphrase=None):
    """
    Generate SSH key pairs (private and public keys).

    :param key_name: Name of the key file to be generated.
    :param passphrase: Passphrase to protect the private key (optional).
    :return: None
    """
    _logger.info(f"Generating SSH key pair for {key_name}.")
    # Generate RSA key
    key = paramiko.RSAKey.generate(2048)

    # Save private key
    private_key_path = os.path.expanduser(f"{constants.ssh_key_path}/{key_name}")
    with open(private_key_path, "w") as private_key_file:
        key.write_private_key(private_key_file, password=passphrase)

    # Save public key
    public_key_path = os.path.expanduser(f"{constants.ssh_key_path}/{key_name}.pub")
    with open(public_key_path, "w") as public_key_file:
        public_key_file.write(f"{key.get_name()} {key.get_base64()}\n")
    _logger.info(f"SSH key pair generated for {key_name}.")
