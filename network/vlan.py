from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from django.http import JsonResponse
from orca_nw_lib.vlan import (
    get_vlan,
    del_vlan,
    config_vlan,
    get_vlan_members,
    add_vlan_mem,
    del_vlan_mem,
)
from orca_nw_lib.common import VlanTagMode


@api_view(["GET", "PUT", "DELETE"])
def vlan_config(request):
    result = []
    http_status = True
    if request.method == "GET":
        device_ip = request.GET.get("mgt_ip", "")
        if not device_ip:
            return Response(
                {"status": "Required field device mgt_ip not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        vlan_name = request.GET.get("name", "")
        data = get_vlan(device_ip, vlan_name)
        if data:
            data["members"]=get_vlan_members(device_ip, vlan_name)
        return JsonResponse(data, safe=False)

    for req_data in (
        request.data
        if isinstance(request.data, list)
        else [request.data]
        if request.data
        else []
    ):
        if request.method == "PUT":
            device_ip = req_data.get("mgt_ip", "")
            if not device_ip:
                return Response(
                    {"status": "Required field device mgt_ip not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            vlan_name = req_data.get("name", "")
            if not vlan_name:
                return Response(
                    {"status": "Required field device vlan_name not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            vlanid = req_data.get("vlanid", "")
            if not vlan_name:
                return Response(
                    {"status": "Required field device vlanid not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                config_vlan(device_ip, vlan_name, vlanid)
                result.append(f"{request.method} request successful :\n {req_data}")
            except Exception as err:
                result.append(
                    f"{request.method} request failed :\n {req_data} \n {str(err)}"
                )
                http_status = http_status and False

            try:
                if members := req_data.get("members"):
                    ## Update members dicxtionary with tagging mode Enum
                    for mem_if, tagging_mode in members.items():
                        members[mem_if] = VlanTagMode.get_enum_from_str(tagging_mode)
                    add_vlan_mem(device_ip, vlan_name, members)
                    result.append(f"{request.method} request successful :\n {members}")
            except Exception as err:
                result.append(
                    f"{request.method} request failed :\n {members} \n {str(err)}"
                )
                http_status = http_status and False

        elif request.method == "DELETE":
            device_ip = req_data.get("mgt_ip", "")
            if not device_ip:
                return Response(
                    {"status": "Required field device mgt_ip not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            vlan_name = req_data.get("name", "")
            if not vlan_name:
                return Response(
                    {"status": "Required field device vlan_name not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if members := req_data.get("members"):
                ## Update members dictionary with tagging mode Enum
                for mem_if, tagging_mode in members.items():
                    try:
                        del_vlan_mem(device_ip, vlan_name, mem_if)
                        result.append(
                            f"{request.method} request successful :\n {members}"
                        )
                    except Exception as err:
                        result.append(
                            f"{request.method} request failed :\n {members} \n {str(err)}"
                        )
                        http_status = http_status and False

            try:
                del_vlan(device_ip, vlan_name)
                result.append(f"{request.method} request successful :\n {req_data}")
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


@api_view(["DELETE"])
def vlan_mem_config(request):
    result = []
    http_status = True
    if request.method == "DELETE":
        for req_data in (
            request.data
            if isinstance(request.data, list)
            else [request.data]
            if request.data
            else []
        ):
            device_ip = req_data.get("mgt_ip", "")
            if not device_ip:
                return Response(
                    {"status": "Required field device mgt_ip not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            vlan_name = req_data.get("name", "")
            if not vlan_name:
                return Response(
                    {"status": "Required field device vlan_name not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if members := req_data.get("members"):
                ## Update members dicxtionary with tagging mode Enum
                for mem_if in members:
                    try:
                        del_vlan_mem(device_ip, vlan_name, mem_if)
                        result.append(
                            f"{request.method} request successful :\n {members}"
                        )
                    except Exception as err:
                        result.append(
                            f"{request.method} request failed :\n {members} \n {str(err)}"
                        )
                        http_status = http_status and False

    return Response(
        {"result": result},
        status=status.HTTP_200_OK
        if http_status
        else status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
