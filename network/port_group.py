""" Port Group API. """
from orca_nw_lib.utils import get_logging
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from orca_nw_lib.common import Speed
from orca_nw_lib.portgroup import (
    get_port_groups,
    get_port_group_members,
    set_port_group_speed, get_port_group_of_interface,
)

from log_manager.decorators import log_request
from log_manager.logger import get_backend_logger
from network.util import (
    add_msg_to_list,
    get_failure_msg,
    get_success_msg,
)

_logger = get_backend_logger()


@api_view(["GET", "PUT"])
@log_request
def port_groups(request):
    """
    This function handles the API view for listing and updating port groups.

    Parameters:
    - request: The HTTP request object.

    Returns:
    - The HTTP response object containing the result of the operation.
    """
    if request.method == "GET":
        device_ip = request.GET.get("mgt_ip", "")
        if not device_ip:
            _logger.error("Required field device mgt_ip not found.")
            return Response(
                {"status": "Required field device mgt_ip not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        port_group_id = request.GET.get("port_group_id", None)
        data = get_port_groups(device_ip, port_group_id)
        return (
            Response(data, status.HTTP_200_OK)
            if data
            else Response({}, status.HTTP_204_NO_CONTENT)
        )
    elif request.method == "PUT":
        result = []
        http_status = True
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
            port_group_id = req_data.get("port_group_id", "")
            if not port_group_id:
                _logger.error("Required field device port_group_id not found.")
                return Response(
                    {"status": "Required field device port_group_id not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            speed = req_data.get("speed", "")
            if not speed:
                _logger.error("Required field device speed not found.")
                return Response(
                    {"status": "Required field device speed not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                set_port_group_speed(
                    device_ip=device_ip, port_group_id=port_group_id, speed=Speed.get_enum_from_str(speed)
                )
                add_msg_to_list(result, get_success_msg(request))
                _logger.info("Set port group speed success.")
            except Exception as err:
                add_msg_to_list(result, get_failure_msg(err, request))
                http_status = http_status and False
                _logger.error("Set port group speed failed.")
    return Response(
        {"result": result},
        status=status.HTTP_200_OK
        if http_status
        else status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


@api_view(
    [
        "GET",
    ]
)
def port_group_members(request):
    """
    This function handles the API view for listing port group members.
    """

    if request.method == "GET":
        device_ip = request.GET.get("mgt_ip", "")
        if not device_ip:
            _logger.error("Required field device mgt_ip not found.")
            return Response(
                {"status": "Required field device mgt_ip not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        port_group_id = request.GET.get("port_group_id", "")
        if not port_group_id:
            _logger.error("Required field device port_group_id not found.")
            return Response(
                {"status": "Required field device port_group_id not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = get_port_group_members(device_ip, port_group_id)
        return (
            Response(data, status.HTTP_200_OK)
            if data
            else Response(
                {"status": "No port group members found."}, status.HTTP_404_NOT_FOUND
            )
        )


@api_view(
    [
        "GET",
    ]
)
def port_group_from_intfc_name(request):
    """
    This function handles the API view for listing port group members.
    """
    if request.method == "GET":
        device_ip = request.GET.get("mgt_ip", "")
        if not device_ip:
            _logger.error("Required field device mgt_ip not found.")
            return Response(
                {"status": "Required field device mgt_ip not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        intf_name = request.GET.get("intf_name", "")
        if not intf_name:
            _logger.error("Required field intf_name not found.")
            return Response(
                {"status": "Required field intf_name not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = get_port_group_of_interface(device_ip, intf_name)
        return (
            Response(data, status.HTTP_200_OK)
            if data
            else Response({"status": "No port group found for the interface."}, status.HTTP_204_NO_CONTENT)
        )
