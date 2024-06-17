""" View for network. """

from celery import shared_task
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from orca_nw_lib.device import get_device_details
from orca_nw_lib.discovery import discover_device
from orca_nw_lib.device_db import delete_device

from log_manager.decorators import log_request, log_task
from network.util import add_msg_to_list, get_failure_msg, get_success_msg, save_log


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
    result = []
    if request.method == "DELETE":
        req_data_list = (
            request.data if isinstance(request.data, list) else [request.data]
        )
        task_id = save_log(req_data_list, request.method)
        delete_db_task.apply_async(
            (req_data_list, request.method, task_id), task_id=task_id
        )
        add_msg_to_list(result,get_success_msg(request.method))
        return Response({"result": result}, status=status.HTTP_100_CONTINUE)


@shared_task
@log_task
def delete_db_task(request, http_method, task_id):
    """
    A function that deletes the database.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        Response: The HTTP response object with the result of the deletion operation.
    """
    result = []
    http_status: bool = True
    if http_method == "DELETE":
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
                    add_msg_to_list(
                        result,
                        get_failure_msg(Exception("Failed to Delete"), http_method),
                    )
                    http_status = False

        except Exception as e:
            add_msg_to_list(
                result, get_failure_msg(e, http_method)
            )
            http_status = False
    return Response(
        {"result": result},
        status=(
            status.HTTP_200_OK if http_status else status.HTTP_500_INTERNAL_SERVER_ERROR
        ),
    )


@api_view(
    [
        "PUT",
    ]
)
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

        task_id = save_log(req_data_list, request.method)
        discover_task.apply_async(
            (req_data_list, request.method, task_id), task_id=task_id
        )
        return Response({"result": "Task Queued"}, status=status.HTTP_100_CONTINUE)


@shared_task
@log_task
def discover_task(request_data: list, method: str, task_id: str):
    result = []
    for req_data in request_data:
        if req_data.get("discover_from_config", False):
            from orca_nw_lib.discovery import discover_device_from_config

            if discover_device_from_config():
                add_msg_to_list(result, get_success_msg(method))
        addresses = (
            req_data.get("address")
            if isinstance(req_data.get("address"), list)
            else [req_data.get("address")]
        )
        for addr in addresses or []:
            if addr and discover_device(ip_or_nw=addr):
                add_msg_to_list(result, get_success_msg(method))

    if not result:
        # Because orca_nw_lib returns report for errors in discovery.
        add_msg_to_list(result, get_success_msg(method))
    else:
        add_msg_to_list(
            result,
            get_failure_msg(
                Exception("Discovery is partially successful or failed."), method
            ),
        )
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
