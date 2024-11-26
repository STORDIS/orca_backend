import os

from fileserver import constants


def get_ztp_path():
    """
    Get the path to the ztp files.

    Returns:
        str: The path to the ztp files.
    """
    app_directory = os.path.dirname(os.path.abspath(__file__))
    ztp_path = os.path.join(app_directory, constants.ztp_path)
    return ztp_path


def get_ztp_files(filename=None) -> list | dict:
    """
    Get ztp files if filename is not None, else get all ztp files.

    Args:
        filename (str, optional): The name of the file to retrieve. Defaults to None.

    Returns:
        list | dict: A list of dictionaries, each containing the content of a ztp file and its name.
    """
    ztp_path = get_ztp_path()
    if filename:
        return _get_ztp_file_content(ztp_path, filename)
    else:
        return [_get_ztp_file_content(ztp_path, f) for f in os.listdir(ztp_path)]


def _get_ztp_file_content(path, filename) -> dict:
    """
    Get the specified file from the ztp files.

    Args:
        path (str): The path to the ztp files.
        filename (str): The name of the file to retrieve.

    Returns:
        dict: A dictionary containing the content of the specified file and its name.
    """
    with open(os.path.join(path, filename), 'r') as f:
        return {"content": f.read(), "filename": filename, "path": f"files/download/ztp/{filename}"}


def add_ztp_file(filename, content):
    """
    Add the specified file to the ztp files.

    Args:
        filename (str): The name of the file to add.
        content (str): The content of the file to add.
    """
    ztp_path = get_ztp_path()
    os.makedirs(ztp_path, exist_ok=True)
    with open(os.path.join(ztp_path, filename), 'w') as f:
        f.write(content)


def delete_ztp_file(filename):
    """
    Delete the specified file from the ztp files.

    Args:
        filename (str): The name of the file to delete.
    """
    ztp_path = get_ztp_path()
    if os.path.exists(os.path.join(ztp_path, filename)):
        os.remove(os.path.join(ztp_path, filename))
