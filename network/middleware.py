from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response

from network.scheduler import discovery_lock


class BlockPutDuringDiscoveryMiddleware:
    """
    Middleware to block PUT operations when device discovery or feature discovery is in progress.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if it's a PUT request and if discovery is in progress
        if request.method == 'PUT':
            if discovery_lock.locked():
                # If the discovery is in progress, block the PUT request
                return JsonResponse(
                    {"result": "Discovery in progress. Please try again later."},
                    status=status.HTTP_409_CONFLICT,
                )

        # Continue processing the request
        response = self.get_response(request)
        return response
