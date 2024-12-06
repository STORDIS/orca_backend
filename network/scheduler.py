import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from log_manager.logger import get_backend_logger
from orca_nw_lib.discovery import trigger_discovery
from network.models import ReDiscoveryConfig
from state_manager.models import ORCABusyState, State

_logger = get_backend_logger()
scheduler = BackgroundScheduler()


def add_scheduler(device_ip, interval):
    """ Adds a new scheduler job for the given device.

    Args:
        device_ip (str): Device IP address.
        interval (int): Interval in minutes.

    Returns:
        None
    """
    scheduler.add_job(
        func=scheduled_discovery,
        trigger='interval',
        minutes=interval,
        max_instances=1,
        args=[device_ip],
        id=f"job_{device_ip}",
        replace_existing=True
    )
    if not scheduler.running:
        scheduler.start()


def remove_scheduler(device_ip):
    """
    Removes a scheduler job for the given device.

    Args:
        device_ip (str): Device IP address.

    Returns:
        None
    """
    job_id = f"job_{device_ip}"
    jobs = scheduler.get_jobs()
    if job_id in [job.id for job in jobs]:
        scheduler.remove_job(f"job_{device_ip}")


def scheduled_discovery(device_ip: str):
    """
    Schedules discovery for the given device.

    Args:
        device_ip (str): Device IP address.

    Returns:
        None
    """
    try:
        state_obj = ORCABusyState.objects.filter(device_ip=device_ip).first()
        if state_obj is None:
            ORCABusyState.update_state(device_ip, State.SCHEDULED_DISCOVERY_IN_PROGRESS)
            trigger_discovery(device_ips=[device_ip])
    except Exception as e:
        _logger.error(f"Failed to schedule discovery on device {device_ip}, Reason: {e}")
    finally:
        ORCABusyState.objects.filter(device_ip=device_ip).delete()
        rediscovery_obj = ReDiscoveryConfig.objects.filter(device_ip=device_ip).first()
        if rediscovery_obj:
            rediscovery_obj.last_discovered = datetime.datetime.now(tz=datetime.timezone.utc)
            rediscovery_obj.save()
