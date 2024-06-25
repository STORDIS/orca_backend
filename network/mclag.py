""" MCLAG API """
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

from orca_nw_lib.common import MclagFastConvergence
from orca_nw_lib.mclag import (
    get_mclags,
    del_mclag,
    config_mclag,
    get_mclag_gw_mac,
    del_mclag_gw_mac,
    config_mclag_gw_mac,
    get_mclag_mem_portchnls,
    config_mclag_mem_portchnl,
    del_mclag_member,
    remove_mclag_domain_fast_convergence,
    add_mclag_domain_fast_convergence
)

from log_manager.decorators import log_request
from network.util import (
    add_msg_to_list,
    get_failure_msg,
    get_success_msg,
)


@api_view(["GET", "PUT", "DELETE"])
@log_request
def device_mclag_list(request):
    """
    Retrieves a list of device MCLAGs.

    Args:
        request: The HTTP request object.

    Returns:
        A Response object containing the list of device MCLAGs.
        If successful, the response will have a status code of 200 (OK).
        If no MCLAGs are found, the response will have a status code of 204 (No Content).
        If there is a bad request, the response will have a status code of 400 (Bad Request).
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
        domain_id = request.GET.get("domain_id", None)
        data = get_mclags(device_ip, domain_id)
        if data and domain_id:
            data["mclag_members"] = get_mclag_mem_portchnls(device_ip, domain_id)
        return (
            Response(data, status=status.HTTP_200_OK)
            if data
            else Response({}, status=status.HTTP_204_NO_CONTENT)
        )
    if request.method == "DELETE":
        for req_data in (
            request.data
            if isinstance(request.data, list)
            else [request.data]
            if request.data
            else []
        ):
            device_ip = req_data.get("mgt_ip", "")
            mclag_members = req_data.get("mclag_members", None)

            if not device_ip:
                return Response(
                    {"status": "Required field device mgt_ip not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # If member are given in the request body
            # Delete the members only, otherwise request is considered
            # to be for deleting the MCLAG
            if mclag_members:
                try:
                    del_mclag_member(device_ip)
                    add_msg_to_list(result, get_success_msg(request))
                except Exception as err:
                    add_msg_to_list(result, get_failure_msg(err, request))
                    http_status = http_status and False
            else:
                try:
                    del_mclag(device_ip)
                    add_msg_to_list(result, get_success_msg(request))
                except Exception as err:
                    add_msg_to_list(result, get_failure_msg(err, request))
                    http_status = http_status and False

    elif request.method == "PUT":
        for req_data in (
            request.data
            if isinstance(request.data, list)
            else [request.data]
            if request.data
            else []
        ):
            device_ip = req_data.get("mgt_ip", "")
            domain_id = req_data.get("domain_id", "")
            src_addr = req_data.get("source_address", "")
            peer_addr = req_data.get("peer_addr", "")
            peer_link = req_data.get("peer_link", "")
            mclag_sys_mac = req_data.get("mclag_sys_mac", "")
            mclag_members = req_data.get("mclag_members", [])
            fast_convergence =  req_data.get("fast_convergence", None)

            if not device_ip or not domain_id:
                return Response(
                    {
                        "result": "All of the required fields mgt_ip, domain_id not found."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if src_addr and peer_addr and peer_link and mclag_sys_mac:
                try:
                    config_mclag(
                        device_ip=device_ip,
                        domain_id=domain_id,
                        source_addr=src_addr,
                        peer_addr=peer_addr,
                        peer_link=peer_link,
                        mclag_sys_mac=mclag_sys_mac,
                        fast_convergence=MclagFastConvergence.get_enum_from_str(fast_convergence),
                    )
                    add_msg_to_list(result, get_success_msg(request))
                except Exception as err:
                    add_msg_to_list(result, get_failure_msg(err, request))
                    http_status = http_status and False

            for mem in mclag_members:
                try:
                    config_mclag_mem_portchnl(device_ip, domain_id, mem)
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


@api_view(["GET", "PUT", "DELETE"])
@log_request
def mclag_gateway_mac(request):
    """
    Retrieves or configures the MCLAG gateway MAC address.

    Args:
        request: The HTTP request object.

    Returns:
        A Response object containing the MCLAG gateway MAC address.
        If successful, the response will have a status code of 200 (OK).
        If no MCLAG gateway MAC address is found, the response will have a status code of 204 (No Content).
        If there is a bad request, the response will have a status code of 400 (Bad Request).
    """
    if request.method == "GET":
        device_ip = request.GET.get("mgt_ip", "")
        if not device_ip:
            return Response(
                {"status": "Required field device mgt_ip not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        gateway_mac = request.GET.get("gateway_mac", "")
        data = get_mclag_gw_mac(device_ip, gateway_mac)
        return (
            Response(data, status=status.HTTP_200_OK)
            if data
            else Response({}, status=status.HTTP_204_NO_CONTENT)
        )
    if request.method == "DELETE":
        device_ip = request.data.get("mgt_ip", "")
        if not device_ip:
            return Response(
                {"status": "Required field device mgt_ip not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            del_mclag_gw_mac(device_ip)
            return Response(
                {"result": get_success_msg(request)},
                status=status.HTTP_200_OK,
            )
        except Exception as err:
            return Response(
                {"result": get_failure_msg(err, request)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    elif request.method == "PUT":
        device_ip = request.data.get("mgt_ip", "")
        if not device_ip:
            return Response(
                {"status": "Required field device mgt_ip not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        gw_mac = request.data.get("gateway_mac", "")
        if not gw_mac:
            return Response(
                {"status": "Required field device mclag_gateway_mac not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            config_mclag_gw_mac(device_ip, gw_mac)
            return Response(
                {"result": get_success_msg(request)},
                status=status.HTTP_200_OK,
            )
        except Exception as err:
            return Response(
                {"result": get_failure_msg(err, request)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@api_view(["POST"])
@log_request
def config_mclag_fast_convergence(request):
    result = []
    http_status = True
    if request.method == "POST":
        for req_data in (
            request.data
            if isinstance(request.data, list)
            else [request.data]
            if request.data
            else []
        ):
            device_ip = req_data.get("mgt_ip", None)
            domain_id = req_data.get("domain_id", None)
            fast_convergence = MclagFastConvergence.get_enum_from_str(req_data.get("fast_convergence", None))
            if not device_ip or not domain_id:
                return Response(
                    {
                        "result": "All of the required fields mgt_ip, domain_id not found."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                if fast_convergence.lower() == MclagFastConvergence.disable:
                    remove_mclag_domain_fast_convergence(device_ip, domain_id)
                    add_msg_to_list(result, get_success_msg(request))
                else:
                    add_mclag_domain_fast_convergence(device_ip, domain_id)
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