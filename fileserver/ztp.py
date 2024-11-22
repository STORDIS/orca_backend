import os

from fileserver import constants


def get_ztp_path():
    app_directory = os.path.dirname(os.path.abspath(__file__))
    ztp_path = os.path.join(app_directory, constants.ztp_path)
    return ztp_path


def get_ztp_files(filename):
    ztp_path = get_ztp_path()
    if filename:
        return _get_ztp_file_content(ztp_path, filename)
    else:
        return [f for f in os.listdir(ztp_path)]


def _get_ztp_file_content(path, filename):
    with open(os.path.join(path, filename), 'r') as f:
        return {"content": f.read(), "filename": filename}


def add_ztp_file(filename, content):
    ztp_path = get_ztp_path()
    os.makedirs(ztp_path, exist_ok=True)
    with open(os.path.join(ztp_path, filename), 'w') as f:
        f.write(content)


def delete_ztp_file(filename):
    ztp_path = get_ztp_path()
    if os.path.exists(os.path.join(ztp_path, filename)):
        os.remove(os.path.join(ztp_path, filename))
