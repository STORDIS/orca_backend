""" View for network. """
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from orca_nw_lib.device import get_device_details
from orca_nw_lib.discovery import discover_all


@api_view(
    [
        "GET",
    ]
)
def discover(request):
    """
    This function is the API view for the 'discover' endpoint.

    Parameters:
        request (HttpRequest): The request object sent by the client.

    Returns:
        Response: The HTTP response containing the result of the API call.
    """
    if request.method == "GET":
        data = discover_all()
        if data:
            return Response({"result": "Success"}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"result": "Fail"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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
        data = get_device_details(request.GET.get("mgt_ip", ""))
        return (
            Response(data, status=status.HTTP_200_OK)
            if data
            else Response({}, status=status.HTTP_204_NO_CONTENT)
        )
