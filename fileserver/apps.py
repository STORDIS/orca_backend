import sys

from django.apps import AppConfig


class FileserverConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fileserver'

    def ready(self):
        if 'runserver' in sys.argv:
            from fileserver.scheduler import add_dhcp_leases_scheduler
            add_dhcp_leases_scheduler()
