import atexit
import os

from apscheduler.schedulers.background import BackgroundScheduler

from fileserver import constants
from fileserver.ssh import ssh_client_with_private_key
from fileserver.models import DHCPServerDetails, DHCPDevices
from log_manager.logger import get_backend_logger
from isc_dhcp_leases import IscDhcpLeases
from orca_nw_lib.device import get_device_details

_logger = get_backend_logger()
scheduler = BackgroundScheduler()


def shutdown_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        _logger.info("DHCP scheduler stopped")


atexit.register(shutdown_scheduler)


def add_dhcp_leases_scheduler(job_id="dhcp_list", trigger="interval", seconds=60):
    global scheduler
    if not scheduler.get_job(job_id):
        scheduler.add_job(
            func=scan_dhcp_leases_file,
            trigger=trigger,
            seconds=seconds,
            id=job_id,
            replace_existing=True,
            max_instances=1,
        )
        _logger.info("DHCP scheduler job added")
    if not scheduler.running:
        scheduler.start()
        _logger.info("DHCP scheduler started")


def scan_dhcp_leases_file():
    """
    Scan the DHCP leases file and update the DHCPDevices table.
    """
    try:
        _logger.info("Scanning DHCP leases file.")
        devices = DHCPServerDetails.objects.all()
        discovered_devices = [device.get("mgt_ip") for device in get_device_details() or None]
        app_directory = os.path.dirname(os.path.abspath(__file__))  # Get the path of the current app
        destination_path = os.path.join(app_directory, 'media/dhcp/dhcpd.leases')
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        for device in devices:
            copy_dhcp_file_to_local(
                ip=device.device_ip,
                username=device.username,
                source_path=constants.dhcp_leases_path,
                destination_path=destination_path
            )
            leases = IscDhcpLeases(destination_path)
            for lease in leases.get():
                _logger.debug("Lease: %s", lease)
                if lease.ip not in discovered_devices and "sonic" in lease.hostname:
                    _logger.debug(f"Discovered sonic device: {lease.ip} - {lease.hostname}")
                    DHCPDevices.objects.update_or_create(
                        device_ip=lease.ip,
                        defaults={
                            'hostname': lease.hostname,
                            'mac_address': lease.ethernet,
                            'dhcp_ip': device.device_ip
                        }
                    )
            _logger.info("Scanned DHCP leases file.")
            # Delete the dhcpd.leases local file.
            if os.path.isfile(destination_path):
                os.remove(destination_path)
    except Exception as e:
        _logger.error(f"Error in scan_dhcp_leases_file: {e}")


def copy_dhcp_file_to_local(ip, username, source_path: str, destination_path: str):
    """
    Copy the specified file from the specified source path to the specified destination path.

    Args:
        ip (str): The IP address of the device.
        username (str): The username to authenticate with the device.
        source_path (str): The source path of the file to copy.
        destination_path (str): The destination path to copy the file to.
    """
    _logger.debug(f"copying file from {source_path} to {destination_path}")
    client = ssh_client_with_private_key(ip, username)
    with client.open_sftp() as sftp:
        sftp.get(source_path, destination_path)
        _logger.debug(f"file copied from {source_path} to {destination_path}")
    client.close()
