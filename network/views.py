""" View for network. """
import datetime

from celery.result import AsyncResult

from orca_backend.celery import cancel_task
from django.forms import model_to_dict
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

from network.models import ReDiscoveryConfig
from network.scheduler import add_scheduler, remove_scheduler
from orca_nw_lib.common import DiscoveryFeature
from orca_nw_lib.device import get_device_details
from orca_nw_lib.discovery import trigger_discovery, discover_nw_features
from log_manager.decorators import log_request
from log_manager.logger import get_backend_logger
from network.util import add_msg_to_list, get_failure_msg, get_success_msg
from state_manager.models import OrcaState

_logger = get_backend_logger()


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
                _logger.info("Deleting device: %s", device_ip)
                del_res = delete_device(device_ip)

                if del_res:
                    add_msg_to_list(result, get_success_msg(request))
                    _logger.debug("Deleted device: %s", device_ip)
                else:
                    add_msg_to_list(result, get_failure_msg(Exception("Failed to Delete"), request))
                    _logger.error("Failed to delete device: %s", device_ip)
                remove_schedular_and_state(device_ip=device_ip)

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
            addresses = req_data.get("address") if isinstance(req_data.get("address"), list) else [
                req_data.get("address")]
            for addr in addresses or []:
                if addr and trigger_discovery(addr):
                    add_msg_to_list(result, get_success_msg(request))
                    _logger.info("Discovered device: %s", addr)

        if not result:
            # Because orca_nw_lib returns report for errors in discovery.
            add_msg_to_list(result, get_success_msg(request))
            _logger.info("Discovery is successful.")
        else:
            add_msg_to_list(result, get_failure_msg(Exception("Discovery is partially successful or failed."), request))
            _logger.error("Discovery is partially successful or failed.")
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
        _logger.debug(data)
        return (
            Response(data, status=status.HTTP_200_OK)
            if data
            else Response({}, status=status.HTTP_204_NO_CONTENT)
        )


@api_view(["PUT"])
@log_request
def discover_by_feature(request):
    """
    This function is an API view that handles the HTTP PUT request for the 'discover_by_feature' endpoint.
    """
    if request.method == "PUT":
        result = []
        req_data_list = (
            request.data if isinstance(request.data, list) else [request.data]
        )
        for req_data in req_data_list:
            device_ip = req_data.get("mgt_ip")
            if not device_ip:
                _logger.error("Required field device mgt_ip not found.")
                return Response(
                    {"result": "Required field device mgt_ip not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            feature = req_data.get("feature")
            if not feature:
                _logger.error("Required field feature not found.")
                return Response(
                    {"result": "Required field feature not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                discover_nw_features(device_ip, DiscoveryFeature.get_enum_from_str(feature))
                add_msg_to_list(result, get_success_msg(request))
                _logger.info("Rediscovered device: %s", device_ip)
            except Exception as e:
                add_msg_to_list(result, get_failure_msg(e, request))
                _logger.error("Failed to rediscover device: %s", device_ip)
        return Response({"result": result}, status=status.HTTP_200_OK)


@api_view(["GET", "PUT", "DELETE"])
@log_request
def discover_scheduler(request):
    """
    This function is an API view that handles the HTTP GET, PUT, and DELETE requests for the 'discover_scheduler' endpoint.
    """
    if request.method == "GET":
        device_ip = request.GET.get("mgt_ip", None)
        if not device_ip:
            _logger.error("Required field device mgt_ip not found.")
            return Response(
                {"result": "Required field device mgt_ip not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = ReDiscoveryConfig.objects.filter(
            device_ip=device_ip
        ).first()
        return (
            Response(model_to_dict(data), status=status.HTTP_200_OK)
            if data
            else Response({}, status=status.HTTP_204_NO_CONTENT)
        )

    if request.method == "PUT":
        result = []
        req_data_list = (
            request.data if isinstance(request.data, list) else [request.data]
        )
        for req_data in req_data_list:
            device_ip = req_data.get("mgt_ip", None)
            if not device_ip:
                _logger.error("Required field device mgt_ip not found.")
                return Response(
                    {"result": "Required field device mgt_ip not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            interval = req_data.get("interval", None)
            if not interval:
                _logger.error("Required field interval not found.")
                return Response(
                    {"result": "Required field interval not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            ReDiscoveryConfig.objects.update_or_create(
                device_ip=device_ip, defaults={
                    "interval": interval,
                    "last_discovered": datetime.datetime.now(tz=datetime.timezone.utc)
                }
            )
            add_scheduler(device_ip, interval)
            _logger.info("scheduler created for device: %s", device_ip)
            add_msg_to_list(result, get_success_msg(request))
        return Response({"result": result}, status=status.HTTP_200_OK)

    if request.method == "DELETE":
        result = []
        req_data_list = (
            request.data if isinstance(request.data, list) else [request.data]
        )
        for req_data in req_data_list:
            device_ip = req_data.get("mgt_ip", None)
            if not device_ip:
                _logger.error("Required field device mgt_ip not found.")
                return Response(
                    {"result": "Required field device mgt_ip not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            ReDiscoveryConfig.objects.filter(device_ip=device_ip).delete()
            remove_scheduler(device_ip)
            add_msg_to_list(result, get_success_msg(request))
            _logger.info("scheduler deleted for device: %s", device_ip)
        return Response({"result": result}, status=status.HTTP_200_OK)


def remove_schedular_and_state(device_ip: str):
    """
    Remove scheduler and state for the given device from database.

    Parameters:
        device_ip (str): The IP address of the device.

    Returns:
        None
    """
    if device_ip:
        # Removing scheduler
        ReDiscoveryConfig.objects.filter(device_ip=device_ip).delete()
        remove_scheduler(device_ip)

        # Removing state
        OrcaState.objects.filter(device_ip=device_ip).delete()
    else:
        # Removing all schedular of all devices
        schedule_objs = ReDiscoveryConfig.objects.all()
        for i in schedule_objs:
            i.delete()
            remove_scheduler(device_ip)

        # Removing all state of all devices
        state_objs = OrcaState.objects.all()
        for i in state_objs:
            i.delete()


@api_view(["DELETE"])
@log_request
def cancel_celery_task(request):
    result = []
    req_data_list = (
        request.data if isinstance(request.data, list) else [request.data]
    )
    for req_data in req_data_list:
        task_id = req_data.get("task_id", None)
        if not task_id:
            _logger.error("Required field device task_id not found.")
            return Response(
                {"result": "Required field device task_id not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        cancel_task(task_id)
        add_msg_to_list(result, get_success_msg(request))
    return Response({"result": result}, status=status.HTTP_200_OK)
