import sys
from django.apps import AppConfig


class StateManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'state_manager'

    def ready(self):
        if 'runserver' in sys.argv:
            from state_manager.models import OrcaState
            OrcaState.objects.all().delete()
