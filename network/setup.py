import json

from django_celery_results.models import TaskResult
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from log_manager.decorators import log_request
from log_manager.logger import get_backend_logger
from network.tasks import install_task, switch_image_task

from network.util import get_success_msg, add_msg_to_list, get_failure_msg
from celery import states, signals


_logger = get_backend_logger()


@api_view(["PUT"])
@log_request
def config_image(request):
    result = []
    http_status = True
    if request.method == "PUT":
        req_data_list = (
            request.data if isinstance(request.data, list) else [request.data]
        )
        for req_data in req_data_list:
            device_ip = req_data.get("mgt_ip", "")
            if not device_ip:
                _logger.error("Required field device mgt_ip not found.")
                return Response(
                    {"status": "Required field device mgt_ip not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            image_name = req_data.get("image_name", "")
            if not req_data.get("image_name"):
                _logger.error("Required field image name not found.")
                return Response(
                    {"status": "Required field image name not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            switch_image_task.apply_async(
                kwargs={"device_ip": device_ip, "image_name": image_name}
            )
            add_msg_to_list(result, get_success_msg(request))
    return Response(
        {"result": result},
        status=(
            status.HTTP_202_ACCEPTED if http_status else status.HTTP_500_INTERNAL_SERVER_ERROR
        ),
    )


@api_view(["PUT"])
@log_request
def install_image(request):
    result = []
    http_status = True
    if request.method == "PUT":
        req_data_list = (
            request.data if isinstance(request.data, list) else [request.data]
        )
        for req_data in req_data_list:
            device_ips = req_data.get("device_ips", "")
            if not device_ips:
                _logger.error("Required field device_ips not found.")
                return Response(
                    {"status": "Required field device_ips not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            image_url = req_data.get("image_url", "")
            if not req_data.get("image_url"):
                _logger.error("Required field image url not found.")
                return Response(
                    {"status": "Required field image url not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            discover_also = req_data.get("discover_also", False)
            try:
                install_task.apply_async(
                    kwargs={
                        "device_ips": device_ips,
                        "image_url": image_url,
                        "discover_also": discover_also,
                        "username": req_data.get("username", None),
                        "password": req_data.get("password", None),
                    }
                )
                add_msg_to_list(result, get_success_msg(request))
            except Exception as err:
                add_msg_to_list(result, get_failure_msg(err, request))
                http_status = http_status and False
                _logger.error(
                    "Failed to install image. Error: %s", err
                )
    return Response(
        {"result": result},
        status=(
            status.HTTP_202_ACCEPTED if http_status else status.HTTP_500_INTERNAL_SERVER_ERROR
        ),
    )


@signals.task_sent.connect
def task_sent(**kwargs):
    TaskResult.objects.store_result(
        task_id=kwargs["task_id"],
        status=states.PENDING,
        content_type="application/json",
        content_encoding="utf-8",
        result=json.dumps({"request_data": kwargs["kwargs"]}),
    )
