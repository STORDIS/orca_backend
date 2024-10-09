from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from log_manager.decorators import log_request
from log_manager.logger import get_backend_logger

from network.util import get_success_msg, add_msg_to_list, get_failure_msg
from orca_nw_lib.setup import install_image_on_device, switch_image_on_device

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
            try:
                output, error = switch_image_on_device(device_ip, image_name)
                if error:
                    add_msg_to_list(result, get_failure_msg(error, request))
                else:
                    add_msg_to_list(result, get_success_msg(request))
                add_msg_to_list(result, get_success_msg(request))
                _logger.info("Successfully changed image on device %s.", device_ip)
            except Exception as err:
                add_msg_to_list(result, get_failure_msg(err, request))
                http_status = http_status and False
                _logger.error("Failed to change image on device %s. Error: %s", device_ip, err)
    return Response(
        {"result": result},
        status=(
            status.HTTP_200_OK if http_status else status.HTTP_500_INTERNAL_SERVER_ERROR
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
                networks = {}
                install_responses = {}
                for i in device_ips:
                    response = install_image_on_device(i, image_url, discover_also)
                    if "error" in response:
                        install_responses[i] = response
                    else:
                        networks[i] = response
                    return Response(
                        {"networks": networks, "install_response": install_responses}
                    )
            except Exception as err:
                add_msg_to_list(result, get_failure_msg(err, request))
                http_status = http_status and False
                _logger.error(
                    "Failed to install image. Error: %s", err
                )
    return Response(
        {"result": result},
        status=(
            status.HTTP_200_OK if http_status else status.HTTP_500_INTERNAL_SERVER_ERROR
        ),
    )

