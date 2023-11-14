from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from orca_nw_lib.device import get_device_details


from orca_nw_lib.discovery import discover_all
from orca_nw_lib.portgroup import (
    get_port_groups,
    get_port_group_members,
)


@api_view(
    [
        "GET",
    ]
)
def discover(request):
    if request.method == "GET":
        data = discover_all()
        if data:
            return JsonResponse({"result": "Success"}, safe=False)
        else:
            return JsonResponse({"result": "Fail"}, safe=False)


@api_view(
    [
        "GET",
    ]
)
def device_list(request):
    if request.method == "GET":
        data = get_device_details(request.GET.get("mgt_ip", ""))
        return JsonResponse(data, safe=False)


@api_view(
    [
        "GET",
    ]
)
def port_groups(request):
    if request.method == "GET":
        device_ip = request.GET.get("mgt_ip", "")
        if not device_ip:
            return Response(
                {"status": "Required field device mgt_ip not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = get_port_groups(device_ip)
        return JsonResponse(data, safe=False)


@api_view(
    [
        "GET",
    ]
)
def port_group_members(request):
    if request.method == "GET":
        device_ip = request.GET.get("mgt_ip", "")
        if not device_ip:
            return Response(
                {"status": "Required field device mgt_ip not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        port_group_id = request.GET.get("port_group_id", "")
        if not port_group_id:
            return Response(
                {"status": "Required field device port_group_id not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = get_port_group_members(device_ip, port_group_id)
        return JsonResponse(data, safe=False)
