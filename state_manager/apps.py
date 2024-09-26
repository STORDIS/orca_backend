import sys

from django.apps import AppConfig


class StateManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'state_manager'

    def ready(self):
        if 'runserver' in sys.argv:
            import datetime
            from orca_nw_lib.device import get_device_details
            from state_manager.models import OrcaState, State
            devices = get_device_details()
            for i in devices:
                OrcaState.objects.update_or_create(
                    device_ip=i.get("mgt_ip"),
                    defaults={
                        "state": str(State.AVAILABLE),
                        "last_updated_time": datetime.datetime.now(
                            tz=datetime.timezone.utc
                        )
                    }
                )
