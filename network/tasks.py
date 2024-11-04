from celery import signals, shared_task, states
from django_celery_results.models import TaskResult

from log_manager.logger import get_backend_logger
from network.util import add_msg_to_list
from orca_nw_lib.setup import switch_image_on_device, install_image_on_device

_logger = get_backend_logger()


@shared_task(track_started=True, trail=True, acks_late=True)
def install_task(device_ips, image_url, discover_also, username, password, http_path):
    """
    Installs an image on a list of devices.
    Args:
        device_ips (list): A list of device IPs.
        image_url (str): The URL of the image to install.
        discover_also (bool): Whether to discover the device.
        username (str): The username to use for authentication.
        password (str): The password to use for authentication.
        http_path (str): The HTTP path of the request.
    Returns:
        dict: A dictionary containing the results of the installation.
    """
    install_responses = {}
    networks = {}
    for device_ip in device_ips:
        try:
            response = install_image_on_device(
                device_ip=device_ip,
                image_url=image_url,
                discover_also=discover_also,
                username=username,
                password=password
            )
            if "output" in response:
                install_responses[device_ip] = response
            else:
                networks[device_ip] = response
        except Exception as err:
            install_responses[device_ip] = {"error": err}
            _logger.error("Failed to install image on device %s. Error: %s", device_ip, err)
    return {"install_responses": install_responses, "networks": networks}


@shared_task(track_started=True, trail=True)
def switch_image_task(device_ip, image_name, http_path):
    """
    Changes the image on a device.
    Args:
        device_ip (str): The IP address of the device.
        image_name (str): The name of the image to change to.
        http_path (str): The HTTP path of the request.
    """
    result = []
    try:
        output, error = switch_image_on_device(device_ip, image_name)
        if error:
            result.append({"message": "failed", "details": error})
        else:
            result.append({"message": "success", "details": output})
            _logger.info("Successfully changed image on device %s.", device_ip)
    except Exception as err:
        add_msg_to_list(result, {"status": "failed", "message": err})
        _logger.error("Failed to change image on device %s. Error: %s", device_ip, err)
    return result


@signals.task_sent.connect
def task_sent(**kwargs):
    """
    Signal handler for task_sent signal.
    Stores the task ID in the database.
    Args:
        kwargs (dict): The keyword arguments passed to the signal handler.
    """
    task_kwargs = kwargs["kwargs"]
    TaskResult.objects.store_result(
        task_id=kwargs["task_id"],
        status=states.PENDING,
        content_type="application/json",
        content_encoding="utf-8",
        result={
            "result": [],
        },
        task_kwargs=task_kwargs,
    )

