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
from orca_nw_lib.port_chnl import (
    get_port_chnl,
    add_port_chnl,
    del_port_chnl,
    get_port_chnl_members,
    add_port_chnl_mem,
    del_port_chnl_mem,
)
from orca_nw_lib.mclag import (
    get_mclags,
    del_mclag,
    config_mclag,
    get_mclag_gw_mac,
    del_mclag_gw_mac,
    config_mclag_gw_mac,
    get_mclag_mem_portchnls,
    config_mclag_mem_portchnl,
    del_mclag_member,
)
from orca_nw_lib.discovery import discover_all
from orca_nw_lib.bgp import get_bgp_global
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


@api_view(["GET", "PUT"])
def device_interfaces_list(request):
    result = []
    http_status = True
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
            try:
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

                result.append(f"{request.method} request successful :\n {req_data}")
                http_status = http_status and True
            except Exception as err:
                result.append(
                    f"{request.method} request failed :\n {req_data} \n {str(err)}"
                )
                http_status = http_status and False

    return Response(
        {"result": result},
        status=status.HTTP_200_OK
        if http_status
        else status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


@api_view(["GET", "PUT", "DELETE"])
def device_port_chnl_list(request):
    result = []
    http_status = True
    if request.method == "GET":
        device_ip = request.GET.get("mgt_ip", "")
        if not device_ip:
            return Response(
                {"status": "Required field device mgt_ip not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        port_chnl_name = request.GET.get("chnl_name", "")
        data = get_port_chnl(device_ip, port_chnl_name)

        for chnl in data if isinstance(data, list) else [data] if data else []:
            chnl["members"] = [
                intf["name"]
                for intf in get_port_chnl_members(device_ip, chnl["lag_name"])
            ]
        return JsonResponse(data, safe=False)

    if request.method == "PUT":
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
            try:
                add_port_chnl(
                    device_ip,
                    req_data.get("chnl_name"),
                    admin_status=req_data.get("admin_status"),
                    mtu=int(req_data.get("mtu")) if "mtu" in req_data else None,
                )
                if members := req_data.get("members"):
                    add_port_chnl_mem(
                        device_ip,
                        req_data.get("chnl_name"),
                        members,
                    )
                result.append(f"{request.method} request successful :\n {req_data}")
                http_status = http_status and True
            except Exception as err:
                result.append(
                    f"{request.method} request failed :\n {req_data} \n {str(err)}"
                )
                http_status = http_status and False

    elif request.method == "DELETE":
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
            try:
                # If member are given in the request body
                # Delete the members only, otherwise request is considered
                # to be for deleting the whole port channel
                if members := req_data.get("members"):
                    for mem in members:
                        del_port_chnl_mem(
                            device_ip,
                            req_data.get("chnl_name"),
                            mem,
                        )
                else:
                    del_port_chnl(device_ip, req_data.get("chnl_name"))

                result.append(f"{request.method} request successful :\n {req_data}")
                http_status = http_status and True
            except Exception as err:
                result.append(
                    f"{request.method} request failed :\n {req_data} \n {str(err)}"
                )
                http_status = http_status and False

    return Response(
        {"result": result},
        status=status.HTTP_200_OK
        if http_status
        else status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


@api_view(["GET", "PUT", "DELETE"])
def device_mclag_list(request):
    result = []
    http_status = True
    if request.method == "GET":
        device_ip = request.GET.get("mgt_ip", "")
        if not device_ip:
            return Response(
                {"status": "Required field device mgt_ip not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        domain_id = request.GET.get("domain_id", None)
        data = get_mclags(device_ip, domain_id)
        if data and domain_id:
            data["mclag_members"] = get_mclag_mem_portchnls(device_ip, domain_id)
        return JsonResponse(data, safe=False)
    if request.method == "DELETE":
        for req_data in (
            request.data
            if isinstance(request.data, list)
            else [request.data]
            if request.data
            else []
        ):
            device_ip = req_data.get("mgt_ip", "")
            mclag_members = req_data.get("mclag_members", None)

            if not device_ip:
                return Response(
                    {"status": "Required field device mgt_ip not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # If member are given in the request body
            # Delete the members only, otherwise request is considered
            # to be for deleting the MCLAG
            if mclag_members:
                try:
                    del_mclag_member(device_ip)
                    result.append(
                        f"{request.method} MCLAG member deletion successful: {req_data}"
                    )
                except Exception as err:
                    result.append(
                        f"{request.method}  MCLAG member deletion failed: {req_data} {str(err)}"
                    )
                    http_status = http_status and False
            else:
                try:
                    del_mclag(device_ip)
                    result.append(
                        f"{request.method} MCLAG deletion successful: {req_data}"
                    )
                except Exception as err:
                    result.append(
                        f"{request.method}  MCLAG deletion failed: {req_data} {str(err)}"
                    )
                    http_status = http_status and False

    elif request.method == "PUT":
        for req_data in (
            request.data
            if isinstance(request.data, list)
            else [request.data]
            if request.data
            else []
        ):
            device_ip = req_data.get("mgt_ip", "")
            domain_id = req_data.get("domain_id", "")
            src_addr = req_data.get("source_address", "")
            peer_addr = req_data.get("peer_addr", "")
            peer_link = req_data.get("peer_link", "")
            mclag_sys_mac = req_data.get("mclag_sys_mac", "")
            mclag_members = req_data.get("mclag_members", [])

            if not device_ip or not domain_id:
                return Response(
                    {
                        "result": "All of the required fields mgt_ip, domain_id not found."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if src_addr and peer_addr and peer_link and mclag_sys_mac:
                try:
                    config_mclag(
                        device_ip,
                        domain_id,
                        src_addr,
                        peer_addr,
                        peer_link,
                        mclag_sys_mac,
                    )
                    result.append(f"{request.method} request successful: {req_data}")
                except Exception as err:
                    result.append(
                        f"{request.method} request failed: {req_data} {str(err)}"
                    )
                    http_status = http_status and False

            for mem in mclag_members:
                try:
                    config_mclag_mem_portchnl(device_ip, domain_id, mem)
                    result.append(f"{request.method} request successful :\n {mem}")
                except Exception as err:
                    result.append(
                        f"{request.method} request failed :\n {mem} {str(err)}"
                    )

    return Response(
        {"result": result},
        status=status.HTTP_200_OK
        if http_status
        else status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


@api_view(["GET", "PUT", "DELETE"])
def mclag_gateway_mac(request):
    if request.method == "GET":
        device_ip = request.GET.get("mgt_ip", "")
        if not device_ip:
            return Response(
                {"status": "Required field device mgt_ip not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        gateway_mac = request.GET.get("gateway_mac", "")
        data = get_mclag_gw_mac(device_ip, gateway_mac)
        return JsonResponse(data, safe=False)
    if request.method == "DELETE":
        device_ip = request.data.get("mgt_ip", "")
        if not device_ip:
            return Response(
                {"status": "Required field device mgt_ip not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            del_mclag_gw_mac(device_ip)
            return Response(
                {"result": f"{request.method} request successful: {request.data}"},
                status=status.HTTP_200_OK,
            )
        except Exception as err:
            return Response(
                {
                    "result": f"{request.method} request failed: {request.data} {str(err)}"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    elif request.method == "PUT":
        device_ip = request.data.get("mgt_ip", "")
        if not device_ip:
            return Response(
                {"status": "Required field device mgt_ip not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        mclag_gateway_mac = request.data.get("gateway_mac", "")
        if not mclag_gateway_mac:
            return Response(
                {"status": "Required field device mclag_gateway_mac not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            config_mclag_gw_mac(device_ip, mclag_gateway_mac)
            return Response(
                {"result": f"{request.method} request successful: {request.data}"},
                status=status.HTTP_200_OK,
            )
        except Exception as err:
            return Response(
                {
                    "result": f"{request.method} request failed: {request.data} {str(err)}"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


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
