import os

from apscheduler.schedulers.background import BackgroundScheduler

from fileserver import constants
from fileserver.dhcp import create_ssh_client
from fileserver.models import DHCPServerDetails, DHCPDevices
from log_manager.logger import get_backend_logger
from isc_dhcp_leases import IscDhcpLeases
from orca_nw_lib.device import get_device_details

_logger = get_backend_logger()
scheduler = BackgroundScheduler()


def add_dhcp_leases_scheduler(job_id="dhcp_list", trigger="interval"):
    scheduler.add_job(
        func=scan_dhcp_leases_file,
        trigger=trigger,
        seconds=constants.dhcp_schedule_interval,
        id=job_id,
        replace_existing=True,
        max_instances=1,
    )
    if not scheduler.running:
        scheduler.start()


def scan_dhcp_leases_file():
    try:
        devices = DHCPServerDetails.objects.all()
        discovered_devices = [device.get("mgt_ip") for device in get_device_details() or None]
        app_directory = os.path.dirname(os.path.abspath(__file__))  # Get the path of the current app
        destination_path = os.path.join(app_directory, 'media/dhcp/dhcpd.leases')
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        for device in devices:
            copy_dhcp_file_to_local(
                ip=device.device_ip,
                username=device.username,
                password=device.password,
                source_path=constants.dhcp_leases_path,
                destination_path=destination_path
            )
            leases = IscDhcpLeases(destination_path)
            for lease in leases.get():
                if lease.ip not in discovered_devices and "sonic" in lease.hostname:
                    DHCPDevices.objects.update_or_create(
                        device_ip=lease.ip,
                        defaults={
                            'hostname': lease.hostname,
                            'mac_address': lease.ethernet,
                            'dhcp_ip': device.device_ip
                        }
                    )
    except Exception as e:
        _logger.error(f"Error in scan_dhcp_leases_file: {e}")


def copy_dhcp_file_to_local(ip, username, password, source_path: str, destination_path: str):
    client = create_ssh_client(ip, username, password)
    with client.open_sftp() as sftp:
        sftp.get(source_path, destination_path)
        _logger.info(f"file copied from {source_path} to {destination_path}")
