""" BGP API views. """
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from orca_nw_lib.bgp import (
    get_bgp_global,
    config_bgp_global,
    del_bgp_global,
    config_bgp_neighbors,
    config_bgp_global_af,
    get_bgp_global_af,
    del_bgp_global_af,
    get_bgp_global_af_network,
    config_bgp_global_af_network,
    del_bgp_global_af_network,
    get_bgp_global_af_aggregate_addr,
    config_bgp_global_af_aggregate_addr,
    del_bgp_global_af_aggregate_addr, delete_all_bgp_neighbor_af, get_bgp_neighbor_sub_interface,
    config_bgp_neighbor_af, get_bgp_neighbor_af, delete_bgp_neighbor, get_bgp_neighbors, get_bgp_neighbor_remote_bgp,
)

from log_manager.decorators import log_request
from log_manager.logger import get_backend_logger
from network.util import (
    add_msg_to_list,
    get_failure_msg,
    get_success_msg,
)

_logger = get_backend_logger()


@api_view(["GET", "PUT", "DELETE"])
@log_request
def device_bgp_global(request):
    """
    A view function that handles GET, PUT, and DELETE requests for device BGP global settings.

    Parameters:
    - request: The request object containing the HTTP request details.

    Returns:
    - If the request method is GET:
        - If the required field "mgt_ip" is not found in the GET parameters, returns a Response object with a "result" field indicating the error and a status code of 400 (Bad Request).
        - Otherwise, returns a Response object with the BGP global settings data retrieved from the device. If no data is found, returns a Response object with an empty dictionary and a status code of 204 (No Content).

    - If the request method is PUT:
        - If the request data is not a list, wraps it in a list.
        - For each request data in the list:
            - If the required field "mgt_ip" is not found, returns a Response object with a "result" field indicating the error and a status code of 400 (Bad Request).
            - If the required field "local_asn" is not found, returns a Response object with a "result" field indicating the error and a status code of 400 (Bad Request).
            - Otherwise, calls the "config_bgp_global" function with the device IP, local ASN, device IP as the router ID, and optional VRF name. Appends the request data to the "result" list if successful, otherwise appends the request data and the error message. Sets the "http_status" flag to False if any request fails.

    - If the request method is DELETE:
        - If the request data is not a list, wraps it in a list.
        - For each request data in the list:
            - If the required field "mgt_ip" is not found, returns a Response object with a "result" field indicating the error and a status code of 400 (Bad Request).
            - If the required field "vrf_name" is not found, returns a Response object with a "result" field indicating the error and a status code of 400 (Bad Request).
            - Otherwise, calls the "del_bgp_global" function with the device IP and VRF name. Appends the request data to the "result" list if successful, otherwise appends the request data and the error message. Sets the "http_status" flag to False if any request fails.

    - Returns a Response object with a "result" field containing the list of results and a status code of 200 (OK) if all requests were successful, otherwise returns a Response object with a status code of 500 (Internal Server Error).
    """
    result = []
    http_status = True
    if request.method == "GET":
        device_ip = request.GET.get("mgt_ip", "")
        if not device_ip:
            _logger.error("Required field device mgt_ip not found.")
            return Response(
                {"result": "Required field device mgt_ip not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = get_bgp_global(device_ip, request.GET.get("vrf_name", None))
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
                _logger.error("Required field device mgt_ip not found.")
                return Response(
                    {"result": "Required field device mgt_ip not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            local_asn = req_data.get("local_asn")
            if not local_asn:
                _logger.error("Required field local_asn not found.")
                return Response(
                    {"result": "Required field local_asn not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                config_bgp_global(
                    device_ip=device_ip,
                    local_asn=local_asn,
                    router_id=req_data.get("router_id"),
                    vrf_name=req_data.get("vrf_name")
                )
                add_msg_to_list(result, get_success_msg(request))
                _logger.info(f"Configured BGP global on {device_ip}.")
            except Exception as err:
                add_msg_to_list(result, get_failure_msg(err, request))
                http_status = http_status and False
                _logger.error("Failed to configure BGP global on %s: %s", device_ip, err)

    elif request.method == "DELETE":
        req_data_list = (
            request.data if isinstance(request.data, list) else [request.data]
        )
        for req_data in req_data_list:
            device_ip = req_data.get("mgt_ip", "")
            if not device_ip:
                _logger.error("Required field device mgt_ip not found.")
                return Response(
                    {"result": "Required field device mgt_ip not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            vrf_name = req_data.get("vrf_name")
            if not vrf_name:
                _logger.error("Required field vrf_name not found.")
                return Response(
                    {"result": "Required field vrf_name not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                del_bgp_global(device_ip, vrf_name)
                add_msg_to_list(result, get_success_msg(request))
                _logger.info(f"Deleted BGP global on {device_ip}.")
            except Exception as err:
                add_msg_to_list(result, get_failure_msg(err, request))
                http_status = http_status and False
                _logger.error("Failed to delete BGP global on %s: %s", device_ip, err)

    return Response(
        {"result": result},
        status=status.HTTP_200_OK
        if http_status
        else status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


@api_view(["GET", "PUT", "DELETE"])
@log_request
def bgp_nbr_config(request):
    """
    A view function that handles GET, PUT, and DELETE requests for BGP neighbor configuration.

    Parameters:
    - request: The request object containing the HTTP request details.

    Returns:
    - If the request method is GET:
        - If the required field "mgt_ip" is not found in the GET parameters, returns a Response object with a "result" field indicating the error and a status code of 400 (Bad Request).
        - If the required field "local_asn" is not found in the GET parameters, returns a Response object with a "result" field indicating the error and a status code of 400 (Bad Request).
        - Otherwise, returns a Response object with the BGP neighbor configuration data retrieved from the device. If no data is found, returns a Response object with an empty dictionary and a status code of 204 (No Content).

    - If the request method is PUT:
        - If the request data is not a list, wraps it in a list.
        - For each request data in the list:
    """
    result = []
    http_status = True
    if request.method == "GET":
        device_ip = request.GET.get("mgt_ip", "")
        if not device_ip:
            _logger.error("Required field device mgt_ip not found.")
            return Response(
                {"result": "Required field device mgt_ip not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = get_bgp_neighbors(
            device_ip=device_ip,
            neighbor_ip=request.GET.get("neighbor_ip", None),
        )
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
                _logger.error("Required field device mgt_ip not found.")
                return Response(
                    {"result": "Required field device mgt_ip not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            remote_asn = req_data.get("remote_asn")
            if not remote_asn:
                _logger.error("Required field remote_asn not found.")
                return Response(
                    {"result": "Required field remote_asn not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            neighbor_ip = req_data.get("neighbor_ip")
            if not neighbor_ip:
                _logger.error("Required field neighbor_ip not found.")
                return Response(
                    {"result": "Required field neighbor_ip not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            vrf_name = req_data.get("vrf_name")
            if not vrf_name:
                _logger.error("Required field remote_vrf not found.")
                return Response(
                    {"result": "Required field remote_vrf not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                config_bgp_neighbors(
                    device_ip=device_ip,
                    remote_asn=remote_asn,
                    neighbor_ip=neighbor_ip,
                    vrf_name=vrf_name,
                    local_asn=req_data.get("local_asn", None),
                    admin_status=req_data.get("admin_status", None),
                )
                add_msg_to_list(result, get_success_msg(request))
                _logger.info(f"Configured BGP neighbor on {device_ip}.")
            except Exception as err:
                _logger.error("Failed to configure BGP neighbor on %s: %s", device_ip, err)
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
                _logger.error("Required field device mgt_ip not found.")
                return Response(
                    {"result": "Required field device mgt_ip not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            neighbor_ip = req_data.get("neighbor_ip", "")
            if not neighbor_ip:
                _logger.error("Required field neighbor_ip not found.")
                return Response(
                    {"result": "Required field neighbor_ip not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                delete_bgp_neighbor(
                    device_ip=device_ip,
                    neighbor_ip=neighbor_ip,
                    vrf_name=req_data.get("vrf_name", ""),
                )
                add_msg_to_list(result, get_success_msg(request))
                _logger.info(f"Deleted BGP neighbor on {device_ip}.")
            except Exception as err:
                _logger.error("Failed to delete BGP neighbor on %s: %s", device_ip, err)
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
def bgp_af(request):
    """
    A view function that handles GET, PUT, and DELETE requests for BGP neighbor configuration.

    Parameters:
    - request: The request object containing the HTTP request details.

    Returns:
    - A Response object containing the BGP neighbor configuration data for the specified device and ASN, or an empty dictionary if no data is found.
    """
    result = []
    http_status = True
    if request.method == "GET":
        device_ip = request.GET.get("mgt_ip", "")
        if not device_ip:
            _logger.error("Required field device mgt_ip not found.")
            return Response(
                {"result": "Required field device mgt_ip not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        local_asn = request.GET.get("local_asn", None)
        if not local_asn:
            _logger.error("Required field device local_asn not found.")
            return Response(
                {"result": "Required field device local_asn not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = get_bgp_global_af(
            device_ip=device_ip,
            asn=local_asn,
            afi_safi=request.GET.get("afi_safi"),
        )
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
                _logger.error("Required field device mgt_ip not found.")
                return Response(
                    {"result": "Required field device mgt_ip not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            afi_safi = req_data.get("afi_safi")
            if not afi_safi:
                _logger.error("Required field afi_safi not found.")
                return Response(
                    {"result": "Required field afi_safi not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            vrf_name = req_data.get("vrf_name")
            if not vrf_name:
                _logger.error("Required field vrf_name not found.")
                return Response(
                    {"result": "Required field vrf_name not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                config_bgp_global_af(
                    device_ip=device_ip,
                    afi_safi=afi_safi,
                    vrf_name=vrf_name,
                    max_ebgp_paths=req_data.get("max_ebgp_paths")
                )
                add_msg_to_list(result, get_success_msg(request))
                _logger.info(f"Configured BGP af on {device_ip}.")
            except Exception as err:
                _logger.error("Failed to configure BGP af on %s.", device_ip)
                add_msg_to_list(result, get_failure_msg(err, request))
                http_status = http_status and False
    elif request.method == "DELETE":
        req_data_list = (
            request.data if isinstance(request.data, list) else [request.data]
        )
        for req_data in req_data_list:
            device_ip = req_data.get("mgt_ip", "")
            if not device_ip:
                _logger.error("Required field device mgt_ip not found.")
                return Response(
                    {"result": "Required field device mgt_ip not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                del_bgp_global_af(
                    device_ip=device_ip,
                    vrf_name=req_data.get("vrf_name"),
                    afi_safi=req_data.get("afi_safi"),
                )
                add_msg_to_list(result, get_success_msg(request))
                _logger.info(f"Deleted BGP af on {device_ip}.")
            except Exception as err:
                _logger.error("Failed to delete BGP af on %s.", device_ip)
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
def bgp_af_network(request):
    """
    A view function that handles GET, PUT, and DELETE requests for BGP neighbor configuration.

    Parameters:
    - request: The request object containing the HTTP request details.

    Returns:
    - A Response object containing the BGP neighbor configuration data for the specified device and ASN, or an empty dictionary if no data is found.
    """
    result = []
    http_status = True
    if request.method == "GET":
        device_ip = request.GET.get("mgt_ip", "")
        if not device_ip:
            _logger.error("Required field device mgt_ip not found.")
            return Response(
                {"result": "Required field device mgt_ip not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        local_asn = request.GET.get("local_asn", None)
        if not local_asn:
            _logger.error("Required field device local_asn not found.")
            return Response(
                {"result": "Required field device local_asn not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = get_bgp_global_af_network(
            device_ip=device_ip,
            asn=local_asn,
            afi_safi=request.GET.get("afi_safi"),
        )
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
                _logger.error("Required field device mgt_ip not found.")
                return Response(
                    {"result": "Required field device mgt_ip not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            afi_safi = req_data.get("afi_safi")
            if not afi_safi:
                _logger.error("Required field afi_safi not found.")
                return Response(
                    {"result": "Required field afi_safi not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            vrf_name = req_data.get("vrf_name")
            if not vrf_name:
                _logger.error("Required field vrf_name not found.")
                return Response(
                    {"result": "Required field vrf_name not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            ip_prefix = req_data.get("ip_prefix")
            try:
                config_bgp_global_af_network(
                    device_ip=device_ip,
                    afi_safi=afi_safi,
                    vrf_name=vrf_name,
                    ip_prefix=ip_prefix
                )
                add_msg_to_list(result, get_success_msg(request))
                _logger.info(f"Configured BGP global on {device_ip}.")
            except Exception as err:
                _logger.error("Failed to configure BGP af network on %s.", device_ip)
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
                    {"result": "Required field device mgt_ip not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                del_bgp_global_af_network(
                    device_ip=device_ip,
                    vrf_name=req_data.get("vrf_name"),
                    afi_safi=req_data.get("afi_safi"),
                    ip_prefix=req_data.get("ip_prefix")
                )
                add_msg_to_list(result, get_success_msg(request))
                _logger.info(f"Deleted BGP af network on {device_ip}.")
            except Exception as err:
                _logger.error("Failed to delete BGP af network on %s.", device_ip)
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
def bgp_af_aggregate_addr(request):
    """
    A view function that handles GET, PUT, and DELETE requests for BGP neighbor configuration.

    Parameters:
    - request: The request object containing the HTTP request details.

    Returns:
    - A Response object containing the BGP neighbor configuration data for the specified device and ASN, or an empty dictionary if no data is found.
    """
    result = []
    http_status = True
    if request.method == "GET":
        device_ip = request.GET.get("mgt_ip", "")
        if not device_ip:
            return Response(
                {"result": "Required field device mgt_ip not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        local_asn = request.GET.get("local_asn", None)
        if not local_asn:
            return Response(
                {"result": "Required field device local_asn not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = get_bgp_global_af_aggregate_addr(
            device_ip=device_ip,
            asn=local_asn,
            afi_safi=request.GET.get("afi_safi"),
        )
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
                _logger.error("Required field device mgt_ip not found.")
                return Response(
                    {"result": "Required field device mgt_ip not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            afi_safi = req_data.get("afi_safi")
            if not afi_safi:
                _logger.error("Required field afi_safi not found.")
                return Response(
                    {"result": "Required field afi_safi not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            vrf_name = req_data.get("vrf_name")
            if not vrf_name:
                _logger.error("Required field vrf_name not found.")
                return Response(
                    {"result": "Required field vrf_name not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            ip_prefix = req_data.get("ip_prefix")
            try:
                config_bgp_global_af_aggregate_addr(
                    device_ip=device_ip,
                    afi_safi=afi_safi,
                    vrf_name=vrf_name,
                    ip_prefix=ip_prefix
                )
                add_msg_to_list(result, get_success_msg(request))
                _logger.info(f"Configured BGP af aggregate address on {device_ip}.")
            except Exception as err:
                _logger.error("Failed to configure BGP af aggregate address on %s.", device_ip)
                add_msg_to_list(result, get_failure_msg(err, request))
                http_status = http_status and False
    elif request.method == "DELETE":
        req_data_list = (
            request.data if isinstance(request.data, list) else [request.data]
        )
        for req_data in req_data_list:
            device_ip = req_data.get("mgt_ip", "")
            if not device_ip:
                _logger.error("Required field device mgt_ip not found.")
                return Response(
                    {"result": "Required field device mgt_ip not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                del_bgp_global_af_aggregate_addr(
                    device_ip=device_ip,
                    vrf_name=req_data.get("vrf_name"),
                    afi_safi=req_data.get("afi_safi"),
                    ip_prefix=req_data.get("ip_prefix")
                )
                add_msg_to_list(result, get_success_msg(request))
                _logger.info(f"Deleted BGP af aggregate address on {device_ip}.")
            except Exception as err:
                _logger.error("Failed to delete BGP af aggregate address on %s.", device_ip)
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
def bgp_neighbor_af(request):
    """
    A view function that handles GET, PUT, and DELETE requests for BGP neighbor configuration.

    Parameters:
    - request: The request object containing the HTTP request details.

    Returns:
    - A Response object containing the BGP neighbor configuration data for the specified device and ASN, or an empty dictionary if no data is found.
    """
    result = []
    http_status = True
    if request.method == "GET":
        device_ip = request.GET.get("mgt_ip", "")
        if not device_ip:
            _logger.error("Required field device mgt_ip not found.")
            return Response(
                {"result": "Required field device mgt_ip not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        neighbor_ip = request.GET.get("neighbor_ip", "")
        if not neighbor_ip:
            _logger.error("Required field neighbor_ip not found.")
            return Response(
                {"result": "Required field neighbor_ip not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = get_bgp_neighbor_af(
            device_ip=device_ip,
            neighbor_ip=neighbor_ip,
            afi_safi=request.GET.get("afi_safi"),
        )
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
                _logger.error("Required field device mgt_ip not found.")
                return Response(
                    {"result": "Required field device mgt_ip not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            afi_safi = req_data.get("afi_safi")
            if not afi_safi:
                _logger.error("Required field afi_safi not found.")
                return Response(
                    {"result": "Required field afi_safi not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            neighbor_ip = req_data.get("neighbor_ip")
            if not neighbor_ip:
                _logger.error("Required field neighbor_ip not found.")
                return Response(
                    {"result": "Required field neighbor_ip not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            vrf_name = req_data.get("vrf_name")
            if not vrf_name:
                _logger.error("Required field vrf_name not found.")
                return Response(
                    {"result": "Required field vrf_name not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                config_bgp_neighbor_af(
                    device_ip=device_ip,
                    afi_safi=afi_safi,
                    vrf=vrf_name,
                    neighbor_ip=neighbor_ip,
                    admin_status=req_data.get("admin_status", True),
                )
                add_msg_to_list(result, get_success_msg(request))
                _logger.info(f"Configured BGP neighbor af on {device_ip}.")
            except Exception as err:
                _logger.error("Failed to configure BGP neighbor af on %s.", device_ip)
                add_msg_to_list(result, get_failure_msg(err, request))
                http_status = http_status and False
    elif request.method == "DELETE":
        req_data_list = (
            request.data if isinstance(request.data, list) else [request.data]
        )
        for req_data in req_data_list:
            device_ip = req_data.get("mgt_ip", "")
            if not device_ip:
                _logger.error("Required field device mgt_ip not found.")
                return Response(
                    {"result": "Required field device mgt_ip not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                delete_all_bgp_neighbor_af(
                    device_ip=device_ip,
                )
                add_msg_to_list(result, get_success_msg(request))
                _logger.info(f"Deleted BGP neighbor af on {device_ip}.")
            except Exception as err:
                _logger.error("Failed to delete BGP neighbor af on %s.", device_ip)
                add_msg_to_list(result, get_failure_msg(err, request))
                http_status = http_status and False

    return Response(
        {"result": result},
        status=status.HTTP_200_OK
        if http_status
        else status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


@api_view(["GET"])
@log_request
def bgp_neighbor_sub_interface(request):
    result = []
    http_status = True
    if request.method == "GET":
        device_ip = request.GET.get("mgt_ip", "")
        if not device_ip:
            _logger.error("Required field device mgt_ip not found.")
            return Response(
                {"result": "Required field device mgt_ip not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        neighbor_ip = request.GET.get("neighbor_ip", "")
        if not neighbor_ip:
            _logger.error("Required field neighbor_ip not found.")
            return Response(
                {"result": "Required field neighbor_ip not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = get_bgp_neighbor_sub_interface(
            device_ip=device_ip,
            neighbor_ip=neighbor_ip,
        )
        return (
            Response(data, status.HTTP_200_OK)
            if data
            else Response({}, status.HTTP_204_NO_CONTENT)
        )

    return Response(
        {"result": result},
        status=status.HTTP_200_OK
        if http_status
        else status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


@api_view(["GET"])
@log_request
def bgp_neighbor_bgp(request):
    result = []
    http_status = True
    if request.method == "GET":
        device_ip = request.GET.get("mgt_ip", "")
        if not device_ip:
            _logger.error("Required field device mgt_ip not found.")
            return Response(
                {"result": "Required field device mgt_ip not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        neighbor_ip = request.GET.get("neighbor_ip", "")
        if not neighbor_ip:
            _logger.error("Required field neighbor_ip not found.")
            return Response(
                {"result": "Required field neighbor_ip not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = get_bgp_neighbor_remote_bgp(
            device_ip=device_ip,
            neighbor_ip=neighbor_ip,
            asn=request.GET.get("asn"),
        )
        return (
            Response(data, status.HTTP_200_OK)
            if data
            else Response({}, status.HTTP_204_NO_CONTENT)
        )

    return Response(
        {"result": result},
        status=status.HTTP_200_OK
        if http_status
        else status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
