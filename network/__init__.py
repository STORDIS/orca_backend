import os
from orca_nw_lib.utils import load_config,load_logging_config

##Loading configuration for network library.
abspath = os.path.abspath(__file__)
# Absolute directory name containing this file
dname = os.path.dirname(abspath)
load_config(f"{dname}/nw_lib_config/orca.yml")
load_logging_config(f"{dname}/nw_lib_config/logging.yml")