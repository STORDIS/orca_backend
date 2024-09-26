import sys
from django.apps import AppConfig


class NetworkConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "network"

    def ready(self):
        if 'runserver' in sys.argv:
            from network.models import ReDiscoveryConfig
            from network.scheduler import add_scheduler
            objs = ReDiscoveryConfig.objects.all()
            for obj in objs:
                add_scheduler(obj.device_ip, obj.interval)
