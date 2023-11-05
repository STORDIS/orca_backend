from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from orca_nw_lib.device import get_device_details
from orca_nw_lib.common import Speed, PortFec
from orca_nw_lib.interface import (
    get_interface,
    config_interface,
)
from orca_nw_lib.port_chnl import get_port_chnl, add_port_chnl, del_port_chnl
from orca_nw_lib.mclag import get_mclags
from orca_nw_lib.discovery import discover_all
from orca_nw_lib.bgp import get_bgp_global
from orca_nw_lib.portgroup import (
    get_port_groups,
    get_port_group_members,
)
from orca_nw_lib.vlan import get_vlan


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
        data = get_interface(device_ip, intfc_name)
        return JsonResponse(data, safe=False)

    elif request.method == "PUT":
        try:
            req_data_list = (
                request.data if isinstance(request.data, list) else [request.data]
            )
            for req_data in req_data_list:
                device_ip = req_data.get("mgt_ip", "")
                if not device_ip:
                    return Response(
                        {"status": "Required field device mgt_ip not found."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                if not req_data.get("name"):
                    return Response(
                        {"status": "Required field name not found."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                config_interface(
                    device_ip=device_ip,
                    intfc_name=req_data.get("name"),
                    loopback=req_data.get("loopback"),
                    enable=True
                    if str(req_data.get("enabled")).lower() == "true"
                    else False
                    if str(req_data.get("enabled")).lower() == "false"
                    else None,
                    mtu=int(req_data.get("mtu")) if "mtu" in req_data else None,
                    description=req_data.get("description"),
                    fec=PortFec.get_enum_from_str(req_data.get("fec")),
                    speed=Speed.get_enum_from_str(req_data.get("speed")),
                )

            return Response({"status": "Config Successful"}, status=status.HTTP_200_OK)
        except Exception as err:
            return Response(
                {"status": err},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@api_view(["GET", "PUT", "DELETE"])
def device_port_chnl_list(request):
    if request.method == "GET":
        device_ip = request.GET.get("mgt_ip", "")
        if not device_ip:
            return Response(
                {"status": "Required field device mgt_ip not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        port_chnl_name = request.GET.get("chnl_name", "")
        data = get_port_chnl(device_ip, port_chnl_name)
        return JsonResponse(data, safe=False)

    elif request.method == "PUT":
        try:
            req_data_list = (
                request.data if isinstance(request.data, list) else [request.data]
            )
            for req_data in req_data_list:
                device_ip = req_data.get("mgt_ip", "")
                if not device_ip:
                    return Response(
                        {"status": "Required field device mgt_ip not found."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                if not req_data.get("chnl_name"):
                    return Response(
                        {"status": "Required field device chnl_name not found."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                add_port_chnl(
                    device_ip,
                    req_data.get("chnl_name"),
                    admin_status=req_data.get("admin_status"),
                    mtu=int(req_data.get("mtu")) if "mtu" in req_data else None,
                )
            return Response({"status": "Config Successful"}, status=status.HTTP_200_OK)
        except Exception as err:
            return Response(
                {"status": err},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    elif request.method == "DELETE":
        try:
            req_data_list = (
                request.data if isinstance(request.data, list) else [request.data]
            )
            for req_data in req_data_list:
                device_ip = req_data.get("mgt_ip", "")
                if not device_ip:
                    return Response(
                        {"status": "Required field device mgt_ip not found."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                if not req_data.get("chnl_name"):
                    return Response(
                        {"status": "Required field device chnl_name not found."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                del_port_chnl(device_ip, req_data.get("chnl_name"))
            return Response({"status": "Config Successful"}, status=status.HTTP_200_OK)
        except Exception as err:
            return Response(
                {"status": err},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
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
        data = get_mclags(device_ip, domain_id)
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
        data = get_bgp_global(device_ip)
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


@api_view(
    [
        "GET",
    ]
)
def vlans(request):
    if request.method == "GET":
        device_ip = request.GET.get("mgt_ip", "")
        if not device_ip:
            return Response(
                {"status": "Required field device mgt_ip not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        vlan_name = request.GET.get("vlan_name", "")
        data = get_vlan(device_ip, vlan_name)
        return JsonResponse(data, safe=False)
