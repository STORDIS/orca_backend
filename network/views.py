import os
from django.shortcuts import render

from django.http import HttpResponse, JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from orca_nw_lib.device import getDeviceDetailsFromDB
from orca_nw_lib.interfaces import (
    getInterfacesDetailsFromDB,
    set_interface_config_on_device,
)
from orca_nw_lib.port_chnl import getPortChnlDetailsFromDB, add_port_chnl_on_device
from orca_nw_lib.mclag import getMCLAGsFromDB
from orca_nw_lib.discovery import discover_all
from orca_nw_lib.bgp import getBGPGlobalJsonFromDB
from orca_nw_lib.portgroup import (
    getJsonOfAllPortGroupsOfDeviceFromDB,
    getJsonOfPortGroupMemIfFromDB,
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
        data = getDeviceDetailsFromDB(request.GET.get("mgt_ip", ""))
        return JsonResponse(data, safe=False)


@api_view(["GET", "PUT"])
def device_interfaces_list(request):
    if request.method == "GET":
        device_ip = request.GET.get("mgt_ip", "")
        if not device_ip:
            return Response(
                {"status": "Required field device mgt_ip not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        intfc_name = request.GET.get("intfc_name", "")
        data = getInterfacesDetailsFromDB(device_ip, intfc_name)
        return JsonResponse(data, safe=False)
    elif request.method == "PUT":
        device_ip = request.POST.get("mgt_ip", "")
        if not device_ip:
            return Response(
                {"status": "Required field device mgt_ip not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        req_data = request.data
        if not req_data.get("name"):
            return Response(
                {"status": "Required field device mgt_ip not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = set_interface_config_on_device(
            device_ip=device_ip,
            intfc_name=req_data.get("name"),
            enable=req_data.get("enabled"),
            mtu=req_data.get("mtu"),
            loopback=req_data.get("loopback-mode"),
            description=req_data.get("description"),
            speed=req_data.get("port-speed"),
        )
        return (
            Response(
                {"status": "Error occurred while applying config."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
            if not data
            else Response({"status": "Config Successful"}, status=status.HTTP_200_OK)
        )
    else:
        return Response(
            {"status": f"Unknown request method {request.method}"},
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["GET", "PUT"])
def device_port_chnl_list(request):
    if request.method == "GET":
        device_ip = request.GET.get("mgt_ip", "")
        if not device_ip:
            return Response(
                {"status": "Required field device mgt_ip not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        port_chnl_name = request.GET.get("chnl_name", "")
        data = getPortChnlDetailsFromDB(device_ip, port_chnl_name)
        return JsonResponse(data, safe=False)
    elif request.method == "PUT":
        device_ip = request.POST.get("mgt_ip", "")
        if not device_ip:
            return Response(
                {"status": "Required field device mgt_ip not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        req_data = request.data
        if not req_data.get("chnl_name"):
            return Response(
                {"status": "Required field device chnl_name not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = add_port_chnl_on_device(
            device_ip,
            req_data.get("chnl_name"),
            admin_status=req_data.get("admin_status"),
            mtu=int(req_data.get("mtu")),
        )
        return (
            Response(
                {"status": "Error occurred while applying config."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
            if not data
            else Response({"status": "Config Successful"}, status=status.HTTP_200_OK)
        )
    else:
        return Response(
            {"status": f"Unknown request method {request.method}"},
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(
    [
        "GET",
    ]
)
def device_mclag_list(request):
    if request.method == "GET":
        device_ip = request.GET.get("mgt_ip", "")
        if not device_ip:
            return Response(
                {"status": "Required field device mgt_ip not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        domain_id = request.GET.get("domain_id", "")
        data = getMCLAGsFromDB(device_ip, domain_id)
        return JsonResponse(data, safe=False)


@api_view(
    [
        "GET",
    ]
)
def device_bgp_global(request):
    if request.method == "GET":
        device_ip = request.GET.get("mgt_ip", "")
        if not device_ip:
            return Response(
                {"status": "Required field device mgt_ip not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = getBGPGlobalJsonFromDB(device_ip)
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
        data = getJsonOfAllPortGroupsOfDeviceFromDB(device_ip)
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
        data = getJsonOfPortGroupMemIfFromDB(device_ip,port_group_id)
        return JsonResponse(data, safe=False)