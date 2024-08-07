from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from log_manager.decorators import log_request
from network.util import add_msg_to_list, get_success_msg, get_failure_msg
from orca_nw_lib.stp_vlan import config_stp_vlan, get_stp_vlan


@api_view(["GET", "PUT"])
@log_request
def stp_vlan_config(request):
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
        data = get_stp_vlan(
            device_ip=device_ip,
            vlan_id=request.GET.get("vlan_id", None)
        )
        return (
            Response(data, status=status.HTTP_200_OK)
            if data
            else Response({}, status=status.HTTP_204_NO_CONTENT)
        )
    for req_data in (request.data if isinstance(request.data, list) else [request.data] if request.data else []):
        if request.method == "PUT":
            device_ip = req_data.get("mgt_ip", "")
            if not device_ip:
                return Response(
                    {"status": "Required field device mgt_ip not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            vlan_id = req_data.get("vlan_id", "")
            if not vlan_id:
                return Response(
                    {"status": "Required field vlan_id not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                config_stp_vlan(
                    device_ip=device_ip,
                    vlan_id=vlan_id,
                    bridge_priority=req_data.get("bridge_priority", None),
                    forwarding_delay=req_data.get("forwarding_delay", None),
                    hello_time=req_data.get("hello_time", None),
                    max_age=req_data.get("max_age", None),
                )
                add_msg_to_list(result, get_success_msg(request))
            except Exception as err:
                add_msg_to_list(result, get_failure_msg(err, request))
                http_status = http_status and False
    return Response(
        {"result": result},
        status=(status.HTTP_200_OK if http_status else status.HTTP_500_INTERNAL_SERVER_ERROR),
    )
