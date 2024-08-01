""" Network Port Channel API. """
import traceback

from orca_nw_lib.common import IFMode
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from orca_nw_lib.port_chnl import (
    get_port_chnl,
    add_port_chnl,
    del_port_chnl,
    get_port_chnl_members,
    add_port_chnl_mem,
    del_port_chnl_mem,
    remove_port_chnl_ip,
    remove_port_channel_vlan_member,
    remove_all_port_channel_vlan_member
)
from log_manager.decorators import log_request
from network.util import add_msg_to_list, get_failure_msg, get_success_msg
from orca_nw_lib.port_chnl import add_port_chnl_vlan_members


@api_view(["GET", "PUT", "DELETE"])
@log_request
def device_port_chnl_list(request):
    """
    Handles the device port channel list API.

    This function is responsible for handling the GET, PUT, and DELETE requests for the device port channel list API. It takes in a `request` object and returns a `Response` object.

    Parameters:
    - `request` (Request): The request object containing the HTTP method and parameters.

    Returns:
    - `Response`: The response object containing the result of the API call.

    Raises:
    - `Exception`: If there is an error during the API call.

    Example Usage:
    ```
    response = device_port_chnl_list(request)
    ```
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
        port_chnl_name = request.GET.get("lag_name", "")
        data = get_port_chnl(device_ip, port_chnl_name)

        for chnl in data if isinstance(data, list) else [data] if data else []:
            chnl["members"] = [
                intf["name"]
                for intf in get_port_chnl_members(device_ip, chnl["lag_name"])
            ]
        return (
            Response(data, status=status.HTTP_200_OK)
            if data
            else Response({}, status=status.HTTP_204_NO_CONTENT)
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
            if not req_data.get("lag_name"):
                return Response(
                    {"status": "Required field device lag_name not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                add_port_chnl(
                    device_ip,
                    req_data.get("lag_name"),
                    admin_status=req_data.get("admin_sts"),
                    mtu=int(req_data.get("mtu")) if "mtu" in req_data else None,
                    static=req_data.get("static", None),
                    min_links=int(req_data.get("min_links")) if "min_links" in req_data else None,
                    fast_rate=req_data.get("fast_rate", None),
                    description=req_data.get("description", None),
                    fallback=req_data.get("fallback", None),
                    graceful_shutdown_mode=req_data.get(
                        "graceful_shutdown_mode", None
                    ),
                    ip_addr_with_prefix=req_data.get("ip_address", None)
                )
                if members := req_data.get("members"):
                    add_port_chnl_mem(
                        device_ip,
                        req_data.get("lag_name"),
                        members,
                    )
                add_msg_to_list(result, get_success_msg(request))
            except Exception as err:
                add_msg_to_list(result, get_failure_msg(err, request))
                http_status = http_status and False

            # some time add port channel vlan members might fail due to L3 configuration etc.
            # hence try catch block and send additional failure message if it fails.
            try:
                if vlan_member := req_data.get("vlan_members"):
                    if_mode = IFMode.get_enum_from_str(vlan_member.get("if_mode"))
                    vlan_ids = vlan_member.get("vlan_ids")
                    print(if_mode, vlan_ids)
                    add_port_chnl_vlan_members(
                        device_ip=device_ip,
                        chnl_name=req_data.get("lag_name"),
                        if_mode=if_mode,
                        vlan_ids=vlan_ids
                    )
            except Exception as err:
                import traceback
                print(traceback.format_exc())
                add_msg_to_list(result, get_failure_msg(err, request))
                http_status = http_status and False

    elif request.method == "DELETE":
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

            try:
                # If member are given in the request body
                # Delete the members only, otherwise request is considered
                # to be for deleting the whole port channel
                if (members := req_data.get("members")) and req_data.get("lag_name"):
                    for mem in members:
                        del_port_chnl_mem(
                            device_ip,
                            req_data.get("lag_name"),
                            mem,
                        )
                else:
                    del_port_chnl(device_ip, req_data.get("lag_name"))
                add_msg_to_list(result, get_success_msg(request))
            except Exception as err:
                add_msg_to_list(result, get_failure_msg(err, request))
                http_status = http_status and False

    return Response(
        {"result": result},
        status=status.HTTP_200_OK
        if http_status
        else status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


@api_view(["DELETE"])
@log_request
def remove_port_channel_ip_address(request):
    """
    Removes IP address from the port channel
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
        chnl_name = req_data.get("lag_name", "")
        if not chnl_name:
            return Response(
                {"status": "Required field device chnl_name not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        ip_addr = req_data.get("ip_address", None)
        try:
            remove_port_chnl_ip(device_ip, chnl_name, ip_addr)
            add_msg_to_list(result, get_success_msg(request))
        except Exception as err:
            add_msg_to_list(result, get_failure_msg(err, request))
            http_status = http_status and False
    return Response(
        {"result": result},
        status=(
            status.HTTP_200_OK if http_status else status.HTTP_500_INTERNAL_SERVER_ERROR
        ),
    )


@api_view(["DELETE"])
@log_request
def remove_port_channel_member_vlan(request):
    """
    Removes vlan member from the port channel
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
        chnl_name = req_data.get("lag_name", "")
        if not chnl_name:
            return Response(
                {"status": "Required field device chnl_name not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        vlan_members = req_data.get("vlan_members", {})
        if_mode = IFMode.get_enum_from_str(vlan_members.get("if_mode"))
        vlan_ids = vlan_members.get("vlan_ids")
        try:
            if if_mode and vlan_ids:
                remove_port_channel_vlan_member(
                    device_ip=device_ip, chnl_name=chnl_name, if_mode=if_mode, vlan_ids=vlan_ids
                )
                add_msg_to_list(result, get_success_msg(request))
            else:
                return Response(
                    {"status": "Required field vlan member not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as err:
            add_msg_to_list(result, get_failure_msg(err, request))
            http_status = http_status and False
    return Response(
        {"result": result},
        status=(
            status.HTTP_200_OK if http_status else status.HTTP_500_INTERNAL_SERVER_ERROR
        ),
    )


@api_view(["DELETE"])
@log_request
def remove_all_port_channel_member_vlan(request):
    """
    Removes all members from the port channel
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
        chnl_name = req_data.get("lag_name", "")
        if not chnl_name:
            return Response(
                {"status": "Required field device chnl_name not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            remove_all_port_channel_vlan_member(
                device_ip=device_ip, chnl_name=chnl_name
            )
            add_msg_to_list(result, get_success_msg(request))
        except Exception as err:
            add_msg_to_list(result, get_failure_msg(err, request))
            http_status = http_status and False
    return Response(
        {"result": result},
        status=(
            status.HTTP_200_OK if http_status else status.HTTP_500_INTERNAL_SERVER_ERROR
        ),
    )
