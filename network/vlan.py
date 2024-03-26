""" VLAN API. """
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from orca_nw_lib.vlan import (
    get_vlan,
    del_vlan,
    config_vlan,
    get_vlan_members,
    add_vlan_mem,
    del_vlan_mem,
)
from orca_nw_lib.common import VlanTagMode

from log_manager.decorators import log_request
from network.util import (
    add_msg_to_list,
    get_failure_msg,
    get_success_msg,
)


@api_view(["GET", "PUT", "DELETE"])
@log_request
def vlan_config(request):
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
        vlan_name = request.GET.get("name", "")
        data = get_vlan(device_ip, vlan_name)
        for vlan_data in data if isinstance(data, list) else [data] if data else []:
            vlan_data["members"] = get_vlan_members(device_ip, vlan_data["name"])
        return (
            Response(data, status=status.HTTP_200_OK)
            if data
            else Response({}, status=status.HTTP_204_NO_CONTENT)
        )

    for req_data in (
        request.data
        if isinstance(request.data, list)
        else [request.data]
        if request.data
        else []
    ):
        if request.method == "PUT":
            device_ip = req_data.get("mgt_ip", "")
            if not device_ip:
                return Response(
                    {"status": "Required field device mgt_ip not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            vlan_name = req_data.get("name", "")
            if not vlan_name:
                return Response(
                    {"status": "Required field device vlan_name not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            vlanid = req_data.get("vlanid", "")
            if not vlan_name:
                return Response(
                    {"status": "Required field device vlanid not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                config_vlan(device_ip, vlan_name, vlanid)
                add_msg_to_list(result, get_success_msg(request, req_data))
            except Exception as err:
                add_msg_to_list(result, get_failure_msg(err, request, req_data))
                http_status = http_status and False

            try:
                if members := req_data.get("members"):
                    ## Update members dicxtionary with tagging mode Enum
                    for mem_if, tagging_mode in members.items():
                        members[mem_if] = VlanTagMode.get_enum_from_str(tagging_mode)
                    add_vlan_mem(device_ip, vlan_name, members)
                    add_msg_to_list(result, get_success_msg(request, req_data))
            except Exception as err:
                add_msg_to_list(result, get_failure_msg(err, request, req_data))
                http_status = http_status and False

        elif request.method == "DELETE":
            device_ip = req_data.get("mgt_ip", "")
            if not device_ip:
                return Response(
                    {"status": "Required field device mgt_ip not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            vlan_name = req_data.get("name", "")
            if vlan_name:
                if members := req_data.get("members"):
                    ## Update members dictionary with tagging mode Enum
                    for mem_if, tagging_mode in members.items():
                        try:
                            del_vlan_mem(device_ip, vlan_name, mem_if)
                            add_msg_to_list(result, get_success_msg(request, req_data))
                        except Exception as err:
                            add_msg_to_list(result, get_failure_msg(err, request, req_data))
                            http_status = http_status and False
            try:
                del_vlan(device_ip, vlan_name)
                add_msg_to_list(result, get_success_msg(request, req_data))
            except Exception as err:
                add_msg_to_list(result, get_failure_msg(err, request, req_data))
                http_status = http_status and False

    return Response(
        {"result": result},
        status=status.HTTP_200_OK
        if http_status
        else status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


@api_view(["DELETE"])
@log_request
def vlan_mem_config(request):
    """
    Deletes VLAN membership configuration.

    Parameters:
    - `request`: The HTTP request object.

    Returns:
    - `Response`: The HTTP response object with the result of the delete operation.
    """
    result = []
    http_status = True
    if request.method == "DELETE":
        for req_data in (
            request.data
            if isinstance(request.data, list)
            else [request.data]
            if request.data
            else []
        ):
            device_ip = req_data.get("mgt_ip", "")
            if not device_ip:
                return Response(
                    {"status": "Required field device mgt_ip not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            vlan_name = req_data.get("name", "")
            if not vlan_name:
                return Response(
                    {"status": "Required field device vlan_name not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if members := req_data.get("members"):
                ## Update members dicxtionary with tagging mode Enum
                for mem_if in members:
                    try:
                        del_vlan_mem(device_ip, vlan_name, mem_if)
                        add_msg_to_list(result, get_success_msg(request, req_data))
                    except Exception as err:
                        add_msg_to_list(result, get_failure_msg(err, request, req_data))
                        http_status = http_status and False

    return Response(
        {"result": result},
        status=status.HTTP_200_OK
        if http_status
        else status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
