import datetime
from enum import Enum, auto

from django.db import models


class OrcaState(models.Model):
    device_ip = models.CharField(max_length=64, primary_key=True)
    state = models.CharField(max_length=64)
    last_updated_time = models.DateTimeField(null=True)

    objects = models.Manager()

    @staticmethod
    def update_state(device_ip, state):
        OrcaState.objects.update_or_create(
            device_ip=device_ip, defaults={
                "state": str(state),
                "last_updated_time": datetime.datetime.now(datetime.timezone.utc)
            }
        )


class State(Enum):
    AVAILABLE = auto()
    DISCOVERY_IN_PROGRESS = auto()
    FEATURE_DISCOVERY_IN_PROGRESS = auto()
    SCHEDULED_DISCOVERY_IN_PROGRESS = auto()
    CONFIG_IN_PROGRESS = auto()

    @staticmethod
    def get_enum_from_str(name: str):
        return State[name] if name in State.__members__ else None

    def __str__(self) -> str:
        return self.name
