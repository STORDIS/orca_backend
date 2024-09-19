from django.apps import AppConfig


class NetworkConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "network"

    def ready(self):
        from network.scheduler import add_scheduler
        from network.models import ReDiscoveryConfig
        objs = ReDiscoveryConfig.objects.all()
        for obj in objs:
            add_scheduler(obj.device_ip)
