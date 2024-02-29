""" Network Port Channel API. """
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
)

from network.util import add_msg_to_list, get_failure_msg, get_success_msg


@api_view(["GET", "PUT", "DELETE"])
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
                )
                if members := req_data.get("members"):
                    add_port_chnl_mem(
                        device_ip,
                        req_data.get("lag_name"),
                        members,
                    )
                add_msg_to_list(result, get_success_msg(request, req_data))
            except Exception as err:
                add_msg_to_list(result, get_failure_msg(err, request, req_data))
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
