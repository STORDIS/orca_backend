import datetime
import json

from django.http import JsonResponse
from django.urls import resolve
from rest_framework import status
from state_manager.models import OrcaState, State


class BlockPutMiddleware:
    """
    Middleware to block PUT operations when device discovery or feature discovery is in progress.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if it's a PUT request and if discovery is in progress
        if request.method == 'PUT':
            ip_next_state = self._get_device_ip_next_state_list(request)
            for ip, next_state in ip_next_state.items():
                state_obj, created = OrcaState.objects.get_or_create(
                    device_ip=ip,
                    defaults={
                        "state": str(State.AVAILABLE)
                    },
                )
                if state_obj.state == str(State.DISCOVERY_IN_PROGRESS):
                    return JsonResponse(
                        {"result": "Discovery in progress"},
                        status=status.HTTP_409_CONFLICT,
                    )
                if state_obj.state == str(State.FEATURE_DISCOVERY_IN_PROGRESS):
                    return JsonResponse(
                        {"result": "Feature discovery in progress"},
                        status=status.HTTP_409_CONFLICT,
                    )
                if state_obj.state == str(State.SCHEDULED_DISCOVERY_IN_PROGRESS):
                    return JsonResponse(
                        {"result": "Scheduled discovery in progress"},
                        status=status.HTTP_409_CONFLICT,
                    )
                if state_obj.state == str(State.CONFIG_IN_PROGRESS):
                    return JsonResponse(
                        {"result": "Config in progress, please try again later"},
                        status=status.HTTP_409_CONFLICT,
                    )
                if state_obj.state == str(State.AVAILABLE):
                    self._update_state(
                        device_ip=ip, state=next_state
                    )
            response = self.get_response(request)
            for ip in ip_next_state.keys():
                self._update_state(device_ip=ip, state=State.AVAILABLE)
        else:
            # Continue processing the request
            response = self.get_response(request)
        return response

    @staticmethod
    def _update_state(device_ip, state):
        OrcaState.update_state(
            device_ip=device_ip,
            state=state,
        )

    @staticmethod
    def _get_device_ip_next_state_list(request):
        url_name = resolve(request.path_info).url_name
        body = json.loads(request.body)
        data = body if isinstance(body, list) else [body]
        result = {}
        if url_name == "discover":
            for i in data:
                address = i.get("address", "all")  # when address is not provided, discover from configured devices
                address_list = address if isinstance(address, list) else [address]
                result.update({i: State.DISCOVERY_IN_PROGRESS for i in address_list})
        if url_name == "discover_by_feature":
            for i in data:
                device_ip = i.get("mgt_ip", "")
                result.update({"device_ip": device_ip, "state": State.FEATURE_DISCOVERY_IN_PROGRESS})
        else:
            for i in data:
                device_ip = i.get("mgt_ip", "")
                result.update({"device_ip": device_ip, "state": State.CONFIG_IN_PROGRESS})
        return result

