""" View for network. """
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from orca_nw_lib.device import get_device_details
from orca_nw_lib.discovery import trigger_discovery

from log_manager.decorators import log_request
from network.util import add_msg_to_list, get_failure_msg, get_success_msg


@api_view(
    [
        "DELETE",
    ]
)
@log_request
def delete_db(request):
    """
    A function that deletes the database.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        Response: The HTTP response object with the result of the deletion operation.
    """
    if request.method == "DELETE":
        from orca_nw_lib.device_db import delete_device
        result = []

        try:
            req_data_list = (
                request.data if isinstance(request.data, list) else [request.data]
            )
            for req_data in req_data_list:
                device_ip = req_data.get("mgt_ip", "") 
                
                del_res = delete_device(device_ip)
                
                if del_res:
                    add_msg_to_list(result, get_success_msg(request))
                else:
                    add_msg_to_list(result,get_failure_msg(Exception("Failed to Delete"),request))
                
        except Exception as e:
            return Response(
                {"result": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        return Response({"result": "Success"}, status=status.HTTP_200_OK)

@api_view(
    [
        "PUT",
    ]
)
@log_request
def discover(request):
    """
    This function is an API view that handles the HTTP PUT request for the 'discover' endpoint.

    Parameters:
        - request: The HTTP request object.

    Returns:
        - Response: The HTTP response object containing the result of the discovery process.
    """
    result = []
    if request.method == "PUT":
        req_data_list = (
            request.data if isinstance(request.data, list) else [request.data]
        )
        for req_data in req_data_list:
            if req_data.get("discover_from_config", False):
                from orca_nw_lib.discovery import discover_device_from_config
                if discover_device_from_config():
                    add_msg_to_list(result, get_success_msg(request))
            addresses= req_data.get("address") if isinstance(req_data.get("address"), list) else [req_data.get("address")]
            for addr in addresses or []:
                if addr and trigger_discovery(addr):
                    add_msg_to_list(result, get_success_msg(request))

        if not result:
            # Because orca_nw_lib returns report for errors in discovery.
            add_msg_to_list(result,get_success_msg(request))
        else:
            add_msg_to_list(result,get_failure_msg(Exception("Discovery is partially successful or failed."),request))
        return Response({"result": result}, status=status.HTTP_200_OK)


@api_view(
    [
        "GET",
    ]
)
def device_list(request):
    """
    A view function that handles the GET request for the device_list endpoint.

    Parameters:
    - request: The Django request object.

    Returns:
    - If successful, returns a JSON response with the device details.
    - If no data is found, returns a JSON response with an empty object and HTTP status code 204.
    """
    if request.method == "GET":
        data = get_device_details(request.GET.get("mgt_ip", None))
        return (
            Response(data, status=status.HTTP_200_OK)
            if data
            else Response({}, status=status.HTTP_204_NO_CONTENT)
        )
