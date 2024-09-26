from django.forms import model_to_dict
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from log_manager.logger import get_backend_logger
from state_manager.models import OrcaState

_logger = get_backend_logger()


@api_view(["GET"])
def get_orca_state(request, device_ip):
    """
    A function that returns the state of the device.

    Parameters:
        request (HttpRequest): The HTTP request object.
        device_ip (str): The IP address of the device.

    Returns:
        Response: The HTTP response object with the result of the state retrieval operation.
    """
    if request.method == "GET":
        if not device_ip:
            _logger.error("Required field device mgt_ip not found.")
            return Response(
                {"result": "Required field device mgt_ip not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = OrcaState.objects.filter(device_ip=device_ip).first()
        return (
            Response(model_to_dict(data), status=status.HTTP_200_OK)
            if data
            else Response({}, status=status.HTTP_204_NO_CONTENT)
        )
