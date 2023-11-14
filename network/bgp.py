from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from orca_nw_lib.bgp import (
    get_bgp_global,
    config_bgp_global,
    del_bgp_global,
    get_bgp_neighbors_subinterfaces,
    get_neighbour_bgp,
    config_bgp_neighbors,
    del_all_bgp_neighbors,
)


@api_view(["GET", "PUT", "DELETE"])
def device_bgp_global(request):
    result = []
    http_status = True
    if request.method == "GET":
        device_ip = request.GET.get("mgt_ip", "")
        if not device_ip:
            return Response(
                {"result": "Required field device mgt_ip not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = get_bgp_global(device_ip, request.GET.get("vrf_name", None))
        return JsonResponse(data, safe=False)
    if request.method == "PUT":
        req_data_list = (
            request.data if isinstance(request.data, list) else [request.data]
        )
        for req_data in req_data_list:
            device_ip = req_data.get("mgt_ip", "")
            if not device_ip:
                return Response(
                    {"result": "Required field device mgt_ip not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            local_asn = req_data.get("local_asn")
            if not local_asn:
                return Response(
                    {"result": "Required field local_asn not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                config_bgp_global(
                    device_ip, local_asn, device_ip, vrf_name=req_data.get("vrf_name")
                )
                result.append(f"{req_data} request successful :\n {req_data}")
            except Exception as err:
                result.append(f"{req_data} request failed :\n {req_data} \n {str(err)}")
                http_status = http_status and False

    elif request.method == "DELETE":
        req_data_list = (
            request.data if isinstance(request.data, list) else [request.data]
        )
        for req_data in req_data_list:
            device_ip = req_data.get("mgt_ip", "")
            if not device_ip:
                return Response(
                    {"result": "Required field device mgt_ip not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            vrf_name = req_data.get("vrf_name")
            if not vrf_name:
                return Response(
                    {"result": "Required field vrf_name not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                del_bgp_global(device_ip, vrf_name)
                result.append(f"{req_data} request successful :\n {req_data}")
            except Exception as err:
                result.append(f"{req_data} request failed :\n {req_data} \n {str(err)}")
                http_status = http_status and False

    return Response(
        {"result": result},
        status=status.HTTP_200_OK
        if http_status
        else status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


@api_view(["GET", "PUT", "DELETE"])
def bgp_nbr_config(request):
    result = []
    http_status = True
    if request.method == "GET":
        device_ip = request.GET.get("mgt_ip", "")
        if not device_ip:
            return Response(
                {"result": "Required field device mgt_ip not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        local_asn = request.GET.get("local_asn", None)
        if not local_asn:
            return Response(
                {"result": "Required field device local_asn not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = {
            "nbr_sub_if": get_bgp_neighbors_subinterfaces(device_ip, local_asn),
            "nbr_bgp": get_neighbour_bgp(device_ip, local_asn),
        }
        return JsonResponse(data, safe=False)
    if request.method == "PUT":
        req_data_list = (
            request.data if isinstance(request.data, list) else [request.data]
        )
        for req_data in req_data_list:
            device_ip = req_data.get("mgt_ip", "")
            if not device_ip:
                return Response(
                    {"result": "Required field device mgt_ip not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            remote_asn = req_data.get("remote_asn")
            if not remote_asn:
                return Response(
                    {"result": "Required field remote_asn not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            neighbor_ip = req_data.get("neighbor_ip")
            if not neighbor_ip:
                return Response(
                    {"result": "Required field neighbor_ip not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            remote_vrf = req_data.get("remote_vrf")
            if not remote_vrf:
                return Response(
                    {"result": "Required field remote_vrf not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                config_bgp_neighbors(device_ip, remote_asn, neighbor_ip, remote_vrf)
                result.append(f"{req_data} request successful :\n {req_data}")
            except Exception as err:
                result.append(f"{req_data} request failed :\n {req_data} \n {str(err)}")
                http_status = http_status and False
    elif request.method == "DELETE":
        req_data_list = (
            request.data if isinstance(request.data, list) else [request.data]
        )
        for req_data in req_data_list:
            device_ip = req_data.get("mgt_ip", "")
            if not device_ip:
                return Response(
                    {"result": "Required field device mgt_ip not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                del_all_bgp_neighbors(device_ip)
                result.append(f"{req_data} request successful :\n {req_data}")
            except Exception as err:
                result.append(f"{req_data} request failed :\n {req_data} \n {str(err)}")
                http_status = http_status and False

    return Response(
        {"result": result},
        status=status.HTTP_200_OK
        if http_status
        else status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
