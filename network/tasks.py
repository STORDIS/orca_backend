import json

from celery import signals, shared_task, states
from django_celery_results.models import TaskResult

from log_manager.logger import get_backend_logger
from network.util import add_msg_to_list
from orca_nw_lib.setup import switch_image_on_device, install_image_on_device

_logger = get_backend_logger()


@shared_task(bind=True, track_started=True, trail=True, acks_late=True)
def install_task(self, device_ips, image_url, discover_also, username, password, http_path):
    install_responses = {}
    networks = {}
    save_default_result(task_id=self.request.id, result={})
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
    return {
        "result": {
            "install_responses": install_responses,
            "networks": networks
        },
        "request_data": {
            "device_ips": device_ips, "image_url": image_url, "discover_also": discover_also
        },
        "http_path": http_path
    }


@shared_task(bind=True, track_started=True, trail=True)
def switch_image_task(self, device_ip, image_name, http_path):
    result = []
    try:
        save_default_result(
            task_id=self.request.id, result={
                "result": result,
                "request_data": {"mgt_ip": device_ip, "image_name": image_name},
                "http_path": http_path
            }
        )
        output, error = switch_image_on_device(device_ip, image_name)
        if error:
            result.append({"message": "failed", "details": error})
        else:
            result.append({"message": "success", "details": output})
            _logger.info("Successfully changed image on device %s.", device_ip)
    except Exception as err:
        add_msg_to_list(result, {"status": "failed", "message": err})
        _logger.error("Failed to change image on device %s. Error: %s", device_ip, err)
    return {
        "result": result,
        "request_data": {"mgt_ip": device_ip, "image_name": image_name},
        "http_path": http_path
    }


@signals.task_sent.connect
def task_sent(**kwargs):
    task_kwargs = kwargs["kwargs"]
    http_path = task_kwargs.pop("http_path", None)
    TaskResult.objects.store_result(
        task_id=kwargs["task_id"],
        status=states.PENDING,
        content_type="application/json",
        content_encoding="utf-8",
        result=json.dumps({"request_data": kwargs["kwargs"], "http_path": http_path}),
    )


def save_default_result(task_id, result):
    task = TaskResult.objects.get(task_id=task_id)
    task.result = json.dumps(result)
    task.save()

