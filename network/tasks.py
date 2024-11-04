import json

from celery import signals, shared_task, states
from celery.result import AsyncResult
from django_celery_results.models import TaskResult

from log_manager.logger import get_backend_logger
from network.util import add_msg_to_list
from orca_nw_lib.setup import switch_image_on_device, install_image_on_device

_logger = get_backend_logger()


@shared_task(bind=True, track_started=True, trail=True, acks_late=True)
def install_task(self, device_ips, image_url, discover_also, username, password, http_path):
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


@shared_task(bind=True, track_started=True, trail=True)
def switch_image_task(self, device_ip, image_name, http_path):
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

