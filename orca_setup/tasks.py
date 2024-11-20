from celery import signals, shared_task, states
from django_celery_results.models import TaskResult

from log_manager.logger import get_backend_logger
from orca_nw_lib.setup import switch_image_on_device, install_image_on_device, scan_networks
import multiprocessing

_logger = get_backend_logger()

# Create a separate process for the worker
multiprocessing.set_start_method('spawn', force=True)


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
    for device_ip in device_ips:
        try:
            response = install_image_on_device(
                device_ip=device_ip,
                image_url=image_url,
                discover_also=discover_also,
                username=username,
                password=password
            )
            install_responses[device_ip] = response
        except Exception as err:
            install_responses[device_ip] = {"error": err}
            _logger.error("Failed to install image on device %s. Error: %s", device_ip, err)
    return install_responses


@shared_task(track_started=True, trail=True, acks_late=True)
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
        result.append({"message": "failed", "details": str(err)})
        _logger.error("Failed to change image on device %s. Error: %s", device_ip, err)
    return result


@shared_task(track_started=True, trail=True, acks_late=True)
def scan_network_task(device_ips: list, **kwargs):
    """
    Scans the network of a device.
    Args:
        device_ips (list): A list of device IPs.
        kwargs (dict): The keyword arguments passed to the task.
    """
    onie_devices = {}
    sonic_devices = {}
    for device_ip in device_ips:
        try:
            onie, sonic = scan_networks(device_ip)
            onie_devices[device_ip] = onie
            sonic_devices[device_ip] = sonic
        except Exception as err:
            onie_devices[device_ip] = {"error": err}
            sonic_devices[device_ip] = {"error": err}
    return {"onie_devices": onie_devices, "sonic_devices": sonic_devices}


@signals.task_sent.connect
def task_sent(**kwargs):
    """
    Signal handler for the Celery task_sent signal.

    This function is triggered whenever a task is dispatched by Celery. It logs
    the task's ID and initial status to the database to facilitate tracking
    throughout its lifecycle. The task status is explicitly set to `PENDING`
    here, as Celery does not automatically set this status at the point of
    dispatch. Celery's task state transitions are typically tracked only after
    task execution begins, so this manual entry of `PENDING` allows the system
    to recognize that the task is awaiting processing right from dispatch.

    Args:
        kwargs (dict): The keyword arguments passed to the signal handler,
                       containing details about the dispatched task, such as
                       task_id and task arguments.
    """
    task_kwargs = kwargs["kwargs"]
    TaskResult.objects.store_result(
        task_id=kwargs["task_id"],
        status=states.PENDING,
        content_type="application/json",
        content_encoding="utf-8",
        result={},
        task_kwargs=task_kwargs,
    )
