from orca_nw_lib.utils import get_logging


def get_backend_logger(path: str = "orca_backend.log"):
    logger = get_logging()
    logger.FileHandler(path)
    return logger.getLogger()
    