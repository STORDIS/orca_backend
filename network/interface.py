""" Interface view. """

from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from orca_nw_lib.interface import get_interface, config_interface, get_pg_of_if,discover_interfaces
from orca_nw_lib.common import Speed, PortFec

from log_manager.decorators import log_request
from network.util import add_msg_to_list, get_failure_msg, get_success_msg


@api_view(["GET", "PUT"])
@log_request
def device_interfaces_list(request):
    """
    This function handles the API view for listing and updating device interfaces.

    Parameters:
    - request: The HTTP request object.

    Returns:
    - The HTTP response object containing the result of the operation.
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
        intfc_name = request.GET.get("name", "")
        data = get_interface(device_ip, intfc_name)
        return (
            Response(data, status.HTTP_200_OK)
            if data
            else Response({}, status.HTTP_204_NO_CONTENT)
        )

    elif request.method == "PUT":
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

            if not req_data.get("name"):
                return Response(
                    {"status": "Required field name not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                config_interface(
                    device_ip=device_ip,
                    if_name=req_data.get("name"),
                    enable=(
                        True
                        if str(req_data.get("enabled")).lower() == "true"
                        else (
                            False
                            if str(req_data.get("enabled")).lower() == "false"
                            else None
                        )
                    ),
                    mtu=int(req_data.get("mtu")) if "mtu" in req_data else None,
                    description=req_data.get("description"),
                    fec=PortFec.get_enum_from_str(req_data.get("fec")),
                    speed=Speed.get_enum_from_str(req_data.get("speed")),
                )
                add_msg_to_list(result, get_success_msg(request, req_data))
                http_status = http_status and True
            except Exception as err:
                add_msg_to_list(result, get_failure_msg(err, request, req_data))
                http_status = http_status and False

    return Response(
        {"result": result},
        status=(
            status.HTTP_200_OK if http_status else status.HTTP_500_INTERNAL_SERVER_ERROR
        ),
    )


@api_view(["GET"])
@log_request
def interface_pg(request):
    """
    A view for listing device interfaces. It takes a GET request and retrieves the device IP and interface name from the request parameters. If the required parameters are not found, it returns a 400 Bad Request response. It then fetches the page of the interface from the device and returns a 200 OK response with the data if it exists, otherwise it returns a 204 No Content response.
    """
    if request.method == "GET":
        device_ip = request.GET.get("mgt_ip", "")
        if not device_ip:
            return Response(
                {"status": "Required field device mgt_ip not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        intfc_name = request.GET.get("name", "")
        if not intfc_name:
            return Response(
                {"status": "Required field device interface name not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = get_pg_of_if(device_ip, intfc_name)
        return (
            Response(data, status.HTTP_200_OK)
            if data
            else Response({}, status.HTTP_204_NO_CONTENT)
        )
    return Response({}, status.HTTP_204_NO_CONTENT)

@api_view(["POST"])
@log_request
def interface_resync(request):
    result = []
    http_status = True
    if request.method == "POST":
        device_ip = request.data.get("mgt_ip", "")
        if not device_ip:
            return Response(
                {"status": "Required field device mgt_ip not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        intfc_name = request.data.get("name", "")

        try:
            discover_interfaces(device_ip, intfc_name)
            add_msg_to_list(result, get_success_msg(request, request.data))
            http_status = http_status and True
        except Exception as err:
            add_msg_to_list(result, get_failure_msg(err, request, request.data))
            http_status = http_status and False
    return Response(
        {"result": result},
        status=(
            status.HTTP_200_OK if http_status else status.HTTP_500_INTERNAL_SERVER_ERROR
        ),
    )