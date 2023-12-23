""" View for network. """
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from orca_nw_lib.device import get_device_details
from orca_nw_lib.discovery import discover_device


@api_view(
    [
        "DELETE",
    ]
)
def delete_db(request):
    """
    A function that deletes the database.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        Response: The HTTP response object with the result of the deletion operation.
    """
    if request.method == "DELETE":
        from orca_nw_lib.utils import clean_db
        try:
            clean_db()
        except Exception as e:
            return Response({"result": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({"result": "Success"}, status=status.HTTP_200_OK)


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
    http_status = True
    if request.method == "PUT":
        req_data_list = (
            request.data if isinstance(request.data, list) else [request.data]
        )
        for req_data in req_data_list:
            if req_data.get("discover_from_config", False):
                from orca_nw_lib.discovery import discover_device_from_config
                if not discover_device_from_config():
                    result.append("Discovery from configuration failed")
                    http_status &= False
            
            
            if addr:=req_data.get("address", ""):
                if not discover_device(ip_or_nw=addr):
                    result.append("Discovery failed for {}".format(addr))
                
        return Response(
            {"result": result},
            status=status.HTTP_200_OK
            if http_status
            else status.HTTP_500_INTERNAL_SERVER_ERROR
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
