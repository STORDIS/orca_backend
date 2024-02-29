import os
from django.apps import AppConfig
from orca_nw_lib.utils import load_orca_config

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
orca_config=f"{dname}/config/orca.yml"
logging_config=f"{dname}/config/logging.yml"

class NetworkConfig(AppConfig):
    name = "network"
    verbose_name = "Network APIs"
    orca_config_loaded = False

    def ready(self):
        if not self.orca_config_loaded:
            load_orca_config(
                orca_config_file=orca_config,
                logging_config_file=logging_config,
                force_reload=False,
            )
            self.orca_config_loaded=True
