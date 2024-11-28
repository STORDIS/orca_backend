import os
import sys

from django.apps import AppConfig


class FileserverConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fileserver'

    def ready(self):
        if 'runserver' in sys.argv:
            os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media'), exist_ok=True)
            from fileserver.scheduler import add_dhcp_leases_scheduler
            from fileserver import constants
            add_dhcp_leases_scheduler(seconds=constants.dhcp_schedule_interval)
