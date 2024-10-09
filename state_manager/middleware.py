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
            ip_next_state = self._get_device_state(request)
            for ip, next_state in ip_next_state.items():
                state_obj, created = OrcaState.objects.get_or_create(
                    device_ip=ip,
                    defaults={"state": str(State.AVAILABLE)},
                )

                # Mapping states to error messages
                state_block_map = {
                    str(State.DISCOVERY_IN_PROGRESS): "Discovery in progress",
                    str(State.FEATURE_DISCOVERY_IN_PROGRESS): "Feature discovery in progress",
                    str(State.SCHEDULED_DISCOVERY_IN_PROGRESS): "Scheduled discovery in progress",
                    str(State.CONFIG_IN_PROGRESS): "Config in progress, please try again later",
                }

                # Check if current state is blocking
                if state_obj.state in state_block_map:
                    return JsonResponse(
                        {"result": state_block_map[state_obj.state]},
                        status=status.HTTP_409_CONFLICT,
                    )

                if state_obj.state == str(State.AVAILABLE):
                    self._update_state(device_ip=ip, state=next_state)

            response = self.get_response(request)

            # Reset state to AVAILABLE after processing
            for ip in ip_next_state.keys():
                self._update_state(device_ip=ip, state=State.AVAILABLE)

        else:
            # Continue processing the request if not PUT
            response = self.get_response(request)

        return response

    @staticmethod
    def _update_state(device_ip, state):
        """
        Updates the OrcaState object with the given device_ip and state.

        Parameters:
            device_ip (str): The IP address of the device.
            state (str): The next state of the device.

        Returns:
            None
        """
        OrcaState.update_state(
            device_ip=device_ip,
            state=str(state),
        )

    @staticmethod
    def _get_device_state(request):
        """
        Returns a dictionary with device_ip as key and next state as value

        Parameters:
            request (HttpRequest): The HTTP request object.

        Returns:
            dict: A dictionary with device_ip as key and next state as value
        """
        url_name = resolve(request.path_info).url_name
        body = json.loads(request.body)
        data = body if isinstance(body, list) else [body]
        result = {}
        if url_name == "discover":
            for i in data:
                address = i.get("address", "all")  # when address is not provided, discover from configured devices
                address_list = address if isinstance(address, list) else [address]
                result.update({i: State.DISCOVERY_IN_PROGRESS for i in address_list})
        elif url_name == "discover_by_feature":
            for i in data:
                device_ip = i.get("mgt_ip", "")
                result.update({device_ip: State.FEATURE_DISCOVERY_IN_PROGRESS})
        else:
            for i in data:
                device_ip = i.get("mgt_ip", "")
                result.update({device_ip: State.CONFIG_IN_PROGRESS})
        return result

