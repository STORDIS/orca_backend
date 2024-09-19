from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler

from log_manager.logger import get_backend_logger
from orca_nw_lib.discovery import discovery_by_feature
from network.models import ReDiscoveryConfig

_logger = get_backend_logger()


def add_scheduler(device_ip, feature):
    scheduler = BackgroundScheduler()
    obj = ReDiscoveryConfig.objects.filter(device_id=device_ip, feature=feature).first()
    scheduler.add_job(
        scheduled_discovery_by_feature, 'interval',
        minutes=obj.interval,
        max_instances=1, args=[device_ip, feature],
        id=f"job_{device_ip}_{feature}"
    )
    scheduler.start()


def scheduled_discovery_by_feature(device_ip, feature):
    try:
        discovery_by_feature(device_ip, feature)
    except Exception as e:
        _logger.error(e)
    obj = ReDiscoveryConfig.objects.filter(device_id=device_ip, feature=feature).first()
    if obj:
        obj.update(last_discovered=datetime.now())
        obj.save()
