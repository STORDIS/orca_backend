import os
from orca_nw_lib.utils import get_logging, get_orca_config

##Loading configuration for network library.
abspath = os.path.abspath(__file__)
# Absolute directory name containing this file
dname = os.path.dirname(abspath)
get_orca_config()
get_logging()