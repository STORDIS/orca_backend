""" View for network. """
from rest_framework.response import Response
from rest_framework import status,permissions
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes


@api_view(
    [
        "GET","PUT","POST","PATCH","DELETE"
    ]
)
@permission_classes((permissions.AllowAny,))
def device_list_123(request):
    """
    A view function that handles the GET request for the device_list endpoint.

    Parameters:
    - request: The Django request object.

    Returns:
    - If successful, returns a JSON response with the device details.
    - If no data is found, returns a JSON response with an empty object and HTTP status code 204.
    """
    # permission_classes = (permissions.AllowAny,)

    if request.method == "GET":
        data = request.data
        return (
            Response(data, status=status.HTTP_200_OK)
            if data
            else Response({}, status=status.HTTP_204_NO_CONTENT)
        )
