import traceback

from rest_framework.decorators import api_view

from log_manager.decorators import log_request
from rest_framework import status
from rest_framework.response import Response

from network.util import add_msg_to_list, get_success_msg, get_failure_msg
from orca_nw_lib.common import STPEnabledProtocol
from orca_nw_lib.stp import (config_stp_global,
                             get_stp_global_config,
                             delete_stp_global_config, delete_stp_global_config_disabled_vlans)


@api_view(["GET", "PUT", "DELETE"])
@log_request
def stp_global_config(request):
    """
    Generates the function comment for the given function body.

    Args:
        request (Request): The request object.

    Returns:
        Response: The response object containing the result of the function.

    Input put request body details:
    mgt_ip (str): The IP address of the device.
    enabled_protocol (list): List of enabled STP protocols. Valid Values: PVST, MSTP, RSTP, RAPID_PVST.
    bpdu_filter (bool): Enable/Disable BPDU filter. Valid Values: True, False.
    bridge_priority (int): The bridge priority value. Valid Range: 0-61440, only multiples of 4096.
    max_age (int): Maximum age value for STP. Valid Range: 6-40.
    hello_time (int): Hello time value for STP. Valid Range: 1-10.
    forwarding_delay (int): Forwarding delay value for STP. Valid Range: 4-30.
    disabled_vlans (list[int], optional): List of disabled VLANs. Defaults to None.
    rootguard_timeout (int, optional): Root guard timeout value. Valid Range to 5-600.
    loop_guard (bool, optional): Enable/Disable loop guard. Valid Values: True, False.
    portfast (bool, optional): Enable/Disable portfast. Valid Values: True, False.
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

        data = get_stp_global_config(device_ip)
        return (
            Response(data if isinstance(data, list) else [data], status=status.HTTP_200_OK)
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
            enabled_protocol = req_data.get("enabled_protocol")
            try:
                config_stp_global(
                    device_ip=device_ip,
                    enabled_protocol=[STPEnabledProtocol.get_enum_from_str(i) for i in enabled_protocol] if enabled_protocol else None,
                    bpdu_filter=req_data.get("bpdu_filter"),
                    forwarding_delay=req_data.get("forwarding_delay"),
                    hello_time=req_data.get("hello_time"),
                    max_age=req_data.get("max_age"),
                    bridge_priority=req_data.get("bridge_priority"),
                    disabled_vlans=req_data.get("disabled_vlans"),
                    rootguard_timeout=req_data.get("rootguard_timeout"),
                    loop_guard=req_data.get("loop_guard"),
                    portfast=req_data.get("portfast"),
                )
                add_msg_to_list(result, get_success_msg(request))
            except Exception as err:
                add_msg_to_list(result, get_failure_msg(err, request))
                http_status = http_status and False
        if request.method == "DELETE":
            device_ip = req_data.get("mgt_ip", "")
            if not device_ip:
                return Response(
                    {"status": "Required field device mgt_ip not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                delete_stp_global_config(device_ip=device_ip)
                add_msg_to_list(result, get_success_msg(request))
            except Exception as err:
                add_msg_to_list(result, get_failure_msg(err, request))
                http_status = http_status and False
    return Response(
        {"result": result},
        status=(status.HTTP_200_OK if http_status else status.HTTP_500_INTERNAL_SERVER_ERROR),
    )


@api_view(["DELETE"])
@log_request
def delete_disabled_vlans(request):
    """
    Deletes disabled VLANs based on the provided request data.
    Parameters:
    - `request` (Request): The request object containing the data for deleting disabled VLANs.
    Returns:
    - `Response`: The response object indicating the result of the deletion operation.
    """
    result = []
    http_status = True
    if request.method == "DELETE":
        req_data = request.data
        device_ip = req_data.get("mgt_ip", "")
        if not device_ip:
            return Response(
                {"status": "Required field device mgt_ip not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        disabled_vlans = req_data.get("disabled_vlans")
        if not disabled_vlans and len(disabled_vlans) == 0:
            return Response(
                {"status": "Required field disabled_vlans not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            delete_stp_global_config_disabled_vlans(device_ip=device_ip, disabled_vlans=disabled_vlans)
            add_msg_to_list(result, get_success_msg(request))
        except Exception as err:
            print(traceback.format_exc())
            add_msg_to_list(result, get_failure_msg(err, request))
            http_status = http_status and False
    return Response(
        {"result": result},
        status=(status.HTTP_200_OK if http_status else status.HTTP_500_INTERNAL_SERVER_ERROR)
    )
