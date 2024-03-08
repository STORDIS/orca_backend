import os
from django.apps import AppConfig
from orca_nw_lib.setup import setup

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
orca_config=f"{dname}/config/orca_nw_lib.yml"
logging_config=f"{dname}/config/orca_nw_lib_logging.yml"

class NetworkConfig(AppConfig):
    name = "network"
    verbose_name = "Network APIs"
    orca_config_loaded = False

    def ready(self):
        if not self.orca_config_loaded:
            setup(
                orca_config_file=orca_config,
                logging_config_file=logging_config,
                force_reload=False,
            )
            self.orca_config_loaded=True
