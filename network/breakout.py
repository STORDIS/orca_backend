from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from log_manager.decorators import log_request
from network.util import add_msg_to_list, get_failure_msg, get_success_msg
from orca_nw_lib.breakout import config_breakout, get_breakout, delete_breakout


@api_view(["PUT", "DELETE", "GET"])
@log_request
def breakout(request):
    """
    Generates the function comment for the given function body.

    Args:
        request (Request): The request object.

    Returns:
        Response: The response object containing the result of the function.
    """
    result = []
    http_status = True
    if request.method == "GET":
        device_ip = request.GET.get("mgt_ip", "")
        if not device_ip:
            return Response(
                {"status": "Required field device mgt_ip not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if_name = request.GET.get("if_name", "")
        if not if_name:
            return Response(
                {"status": "Required field device interface name not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = get_breakout(device_ip, if_name)
        return (
            Response(data, status.HTTP_200_OK)
            if data
            else Response({}, status.HTTP_204_NO_CONTENT)
        )
    if request.method == "PUT":
        req_data_list = (
            request.data if isinstance(request.data, list) else [request.data]
        )
        for req_data in req_data_list:
            device_ip = req_data.get("mgt_ip", "")
            if not device_ip:
                return Response(
                    {"status": "Required field device mgt_ip not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if_alias = req_data.get("if_alias", "")
            if not if_alias:
                return Response(
                    {"status": "Required field device interface alias name not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if_name = req_data.get("if_name", "")
            if not if_name:
                return Response(
                    {"status": "Required field device interface name not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                config_breakout(
                    device_ip=device_ip,
                    if_alias=if_alias,
                    if_name=if_name,
                    index=req_data.get("index", None),
                    num_breakouts=req_data.get("num_breakouts", None),
                    breakout_speed=req_data.get("breakout_speed", None),
                    num_physical_channels=req_data.get("num_physical_channels", None)
                )
                add_msg_to_list(result, get_success_msg(request))
            except Exception as err:
                add_msg_to_list(result, get_failure_msg(err, request))
                http_status = http_status and False

    if request.method == "DELETE":
        req_data_list = (
            request.data if isinstance(request.data, list) else [request.data]
        )
        for req_data in req_data_list:
            device_ip = req_data.get("mgt_ip", "")
            if not device_ip:
                return Response(
                    {"status": "Required field device mgt_ip not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if_name = req_data.get("if_name", "")
            if not if_name:
                return Response(
                    {"status": "Required field device interface name not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                delete_breakout(device_ip=device_ip, if_name=if_name)
                add_msg_to_list(result, get_success_msg(request))
            except Exception as err:
                import traceback
                print(traceback.format_exc())
                add_msg_to_list(result, get_failure_msg(err, request))
                http_status = http_status and False

    return Response(
        {"result": result},
        status=(
            status.HTTP_200_OK if http_status else status.HTTP_500_INTERNAL_SERVER_ERROR
        ),
    )