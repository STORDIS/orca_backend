""" VLAN API. """
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from orca_nw_lib.vlan import (
    get_vlan,
    del_vlan,
    config_vlan,
    get_vlan_members,
    del_vlan_mem,
    remove_ip_from_vlan,
    remove_anycast_ip_from_vlan,
)
from orca_nw_lib.common import IFMode, VlanAutoState

from log_manager.decorators import log_request
from log_manager.logger import get_backend_logger
from network.util import (
    add_msg_to_list,
    get_failure_msg,
    get_success_msg,
)
from network.models import IPAvailability


_logger = get_backend_logger()


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
            _logger.error("Required field device mgt_ip not found.")
            return Response(
                {"status": "Required field device mgt_ip not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        vlan_name = request.GET.get("name", "")
        data = get_vlan(device_ip, vlan_name)
        for vlan_data in data if isinstance(data, list) else [data] if data else []:
            vlan_data["mem_ifs"] = get_vlan_members(device_ip, vlan_data["name"])
            for mem_if in vlan_data["mem_ifs"]:
                vlan_data["mem_ifs"][mem_if] = str(vlan_data["mem_ifs"][mem_if])

        return (
            Response(data, status=status.HTTP_200_OK)
            if data
            else Response({}, status=status.HTTP_204_NO_CONTENT)
        )

    for req_data in (
        request.data
        if isinstance(request.data, list)
        else [request.data] if request.data else []
    ):
        if request.method == "PUT":
            device_ip = req_data.get("mgt_ip", "")
            if not device_ip:
                _logger.error("Required field device mgt_ip not found.")
                return Response(
                    {"status": "Required field device mgt_ip not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            vlan_name = req_data.get("name", "")
            if not vlan_name:
                _logger.error("Required field device vlan_name not found.")
                return Response(
                    {"status": "Required field device vlan_name not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            members = {}
            if mem := req_data.get("mem_ifs"):
                ## Update members dictionary with tagging mode Enum
                for mem_if, tagging_mode in mem.items():
                    members[mem_if] = IFMode.get_enum_from_str(tagging_mode)
            ip_addr_with_prefix = req_data.get("ip_address", None)
            anycast_ip_addr_with_prefix = req_data.get("sag_ip_address", None)
            try:
                config_vlan(
                    device_ip,
                    vlan_name,
                    enabled=req_data.get("enabled", None),
                    descr=req_data.get("description", None),
                    mtu=req_data.get("mtu", None),
                    ip_addr_with_prefix=ip_addr_with_prefix,
                    autostate=(
                        auto_st
                        if (
                            auto_st := VlanAutoState.get_enum_from_str(
                                req_data.get("autostate")
                            )
                        )
                        else None
                    ),
                    anycast_addr=req_data.get("sag_ip_address", None),
                    mem_ifs=members if members else None,
                )
                if ip_addr_with_prefix:
                    # removing ip usage for vlan if usage for vlan exits
                    IPAvailability.remove_usage_by_device_ip_and_used_in(device_ip, vlan_name)
                    # adding ip usage
                    IPAvailability.add_ip_usage(ip=ip_addr_with_prefix, device_ip=device_ip, used_in=vlan_name)
                if anycast_ip_addr_with_prefix:
                    # anycast ip is list so can be updated without removing ip usage.
                    for ip in anycast_ip_addr_with_prefix:
                        IPAvailability.add_ip_usage(ip=ip, device_ip=device_ip, used_in=vlan_name)
                add_msg_to_list(result, get_success_msg(request))
                _logger.info("Successfully configured VLAN: %s", vlan_name)
            except Exception as err:
                add_msg_to_list(result, get_failure_msg(err, request))
                http_status = http_status and False
                _logger.error("Failed to configure VLAN: %s", vlan_name)

        elif request.method == "DELETE":
            device_ip = req_data.get("mgt_ip", "")
            if not device_ip:
                _logger.error("Required field device mgt_ip not found.")
                return Response(
                    {"status": "Required field device mgt_ip not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            vlan_name = req_data.get("name", "")
            if vlan_name:
                if members := req_data.get("mem_ifs"):
                    ## Update members dictionary with tagging mode Enum
                    for mem_if, tagging_mode in members.items():
                        try:
                            del_vlan_mem(
                                device_ip,
                                vlan_name,
                                mem_if,
                            )
                            add_msg_to_list(result, get_success_msg(request))
                            _logger.info("Successfully deleted VLAN member: %s", mem_if)
                        except Exception as err:
                            add_msg_to_list(result, get_failure_msg(err, request))
                            http_status = http_status and False
                            _logger.error("Failed to delete VLAN member: %s", mem_if)
            try:
                del_vlan(device_ip, vlan_name)
                IPAvailability.remove_usage_by_device_ip_and_used_in(device_ip, vlan_name)
                add_msg_to_list(result, get_success_msg(request))
                _logger.info("Successfully deleted VLAN: %s", vlan_name)
            except Exception as err:
                add_msg_to_list(result, get_failure_msg(err, request))
                http_status = http_status and False
                _logger.error("Failed to delete VLAN: %s", vlan_name)

    return Response(
        {"result": result},
        status=(
            status.HTTP_200_OK if http_status else status.HTTP_500_INTERNAL_SERVER_ERROR
        ),
    )


@api_view(["DELETE"])
@log_request
def remove_vlan_ip_address(request):
    result = []
    http_status = True
    if request.method == "DELETE":
        req_data = request.data
        device_ip = req_data.get("mgt_ip", "")
        if not device_ip:
            _logger.error("Required field device mgt_ip not found.")
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
        ip_address = req_data.get("ip_address", None)
        try:
            remove_ip_from_vlan(
                device_ip,
                vlan_name,
            )
            if ip_address:
                IPAvailability.add_ip_usage(ip=ip_address, device_ip=None, used_in=None)
            else:
                IPAvailability.remove_usage_by_device_ip_and_used_in(device_ip, vlan_name)
            _logger.info("Successfully removed IP address from VLAN: %s", vlan_name)
        except Exception as err:
            add_msg_to_list(result, get_failure_msg(err, request))
            http_status = http_status and False
            _logger.error("Failed to remove IP address from VLAN: %s", vlan_name)

        if sag_ip_address:=req_data.get("sag_ip_address", []):
            for sag_ip in sag_ip_address:
                try:
                    remove_anycast_ip_from_vlan(device_ip, vlan_name, sag_ip)
                    add_msg_to_list(result, get_success_msg(request))
                    if ip_address:
                        IPAvailability.add_ip_usage(ip=ip_address, device_ip=None, used_in=None)
                    else:
                        IPAvailability.remove_usage_by_device_ip_and_used_in(device_ip, vlan_name)
                    add_msg_to_list(result, get_success_msg(request))
                    _logger.info("Successfully removed anycast IP address from VLAN: %s", vlan_name)
                except Exception as err:
                    add_msg_to_list(result, get_failure_msg(err, request))
                    http_status = http_status and False
                    _logger.error("Failed to remove anycast IP address from VLAN: %s", vlan_name)
    return Response(
        {"result": result},
        status=(
            status.HTTP_200_OK if http_status else status.HTTP_500_INTERNAL_SERVER_ERROR
        ),
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
            else [request.data] if request.data else []
        ):
            device_ip = req_data.get("mgt_ip", "")
            if not device_ip:
                _logger.error("Required field device mgt_ip not found.")
                return Response(
                    {"status": "Required field device mgt_ip not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            vlan_name = req_data.get("name", "")
            if not vlan_name:
                _logger.error("Required field device vlan_name not found.")
                return Response(
                    {"status": "Required field device vlan_name not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if members := req_data.get("mem_ifs"):
                ## Update members dicxtionary with tagging mode Enum
                for mem_if, if_mode in members.items():
                    try:
                        del_vlan_mem(device_ip, vlan_name, mem_if)
                        add_msg_to_list(result, get_success_msg(request))
                        _logger.info("Successfully deleted VLAN member: %s", mem_if)
                    except Exception as err:
                        add_msg_to_list(result, get_failure_msg(err, request))
                        http_status = http_status and False
                        _logger.error("Failed to delete VLAN member: %s", mem_if)

    return Response(
        {"result": result},
        status=(
            status.HTTP_200_OK if http_status else status.HTTP_500_INTERNAL_SERVER_ERROR
        ),
    )
