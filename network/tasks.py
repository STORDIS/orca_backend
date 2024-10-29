import time

from celery import signals, shared_task

from log_manager.logger import get_backend_logger
from network.util import add_msg_to_list
from orca_nw_lib.setup import switch_image_on_device, install_image_on_device

_logger = get_backend_logger()


@shared_task(track_started=True, trail=True, acks_late=True)
def install_task(device_ips, image_url, discover_also, username, password):
    result = []
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
                result.append({"message": "success", "details": {"install_response": response}})
            else:
                result.append({"message": "success", "details": {"device_ips": response}})
        except Exception as err:
            add_msg_to_list(result, {"status": "failed", "message": err})
            _logger.error("Failed to install image on device %s. Error: %s", device_ip, err)
    return {
        "result": result,
        "request_data": {
            "device_ips": device_ips, "image_url": image_url, "discover_also": discover_also
        }
    }



@shared_task(track_started=True, trail=True)
def switch_image_task(device_ip, image_name):
    result = []
    try:
        time.sleep(60)
        output, error = switch_image_on_device(device_ip, image_name)
        if error:
            result.append({"message": "failed", "details": error})
        else:
            result.append({"message": "success", "details": output})
            _logger.info("Successfully changed image on device %s.", device_ip)
    except Exception as err:
        add_msg_to_list(result, {"status": "failed", "message": err})
        _logger.error("Failed to change image on device %s. Error: %s", device_ip, err)
    return {"result": result, "request_data": {"mgt_ip": device_ip, "image_name": image_name}}


