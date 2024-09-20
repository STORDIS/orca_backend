import threading
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler

from log_manager.logger import get_backend_logger
from orca_nw_lib.discovery import trigger_discovery
from network.models import ReDiscoveryConfig

_logger = get_backend_logger()
scheduler = BackgroundScheduler()
discovery_lock = threading.Lock()


def add_scheduler(device_ip):
    obj = ReDiscoveryConfig.objects.get(device_ip=device_ip)
    scheduler.add_job(
        scheduled_discovery, 'interval',
        minutes=obj.interval,
        max_instances=1,
        args=[device_ip],
        id=f"job_{device_ip}",
        replace_existing=True
    )
    if not scheduler.running:
        scheduler.start()


def remove_scheduler(device_ip):
    job_id = f"job_{device_ip}"
    jobs = scheduler.get_jobs()
    if job_id in [job.id for job in jobs]:
        scheduler.remove_job(f"job_{device_ip}")


def scheduled_discovery(device_ip):
    try:
        with discovery_lock:
            trigger_discovery(device_ip)
    except Exception as e:
        _logger.error(e)
    obj = ReDiscoveryConfig.objects.get(device_ip=device_ip)
    if obj:
        obj.last_discovered = datetime.now()
        obj.save()
