from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from log_manager.decorators import log_request
from network.util import add_msg_to_list, get_success_msg, get_failure_msg
from orca_nw_lib.common import STPPortEdgePort, STPPortLinkType, STPPortGuard
from orca_nw_lib.stp_port import add_stp_port_members, get_stp_port_members, delete_stp_port_member


@api_view(["PUT", "GET", "DELETE"])
@log_request
def stp_port_config(request):
    """"""
    result = []
    http_status = True
    if request.method == "GET":
        device_ip = request.GET.get("mgt_ip", "")
        if not device_ip:
            return Response(
                {"status": "Required field device mgt_ip not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if_name = request.GET.get("if_name", None)
        data = get_stp_port_members(device_ip, if_name)
        return (
            Response(data, status=status.HTTP_200_OK)
            if data
            else Response({}, status=status.HTTP_204_NO_CONTENT)
        )
    for req_data in (request.data if isinstance(request.data, list) else [request.data] if request.data else []):
        if request.method == "PUT":
            device_ip = req_data.get("mgt_ip", "")
            if not device_ip:
                return Response(
                    {"status": "Required field device mgt_ip not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if_name = req_data.get("if_name", None)
            if not if_name:
                return Response(
                    {"status": "Required field if_name not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            edge_port = req_data.get("edge_port", None)
            link_type = req_data.get("link_type", None)
            guard = req_data.get("guard", None)
            bpdu_guard = req_data.get("bpdu_guard", None)
            bpdu_filter = req_data.get("bpdu_filter", None)
            port_fast = req_data.get("portfast", None)
            uplink_fast = req_data.get("uplink_fast", None)
            bpdu_guard_port_shutdown = req_data.get("bpdu_guard_port_shutdown", None)
            cost = req_data.get("cost", None)
            port_priority = req_data.get("port_priority", None)
            stp_enabled = req_data.get("stp_enabled", None)
            try:
                add_stp_port_members(
                    device_ip=device_ip,
                    if_name=if_name,
                    edge_port=STPPortEdgePort.get_enum_from_str(edge_port) if edge_port else None,
                    link_type=STPPortLinkType.get_enum_from_str(link_type)if link_type else None,
                    guard=STPPortGuard.get_enum_from_str(guard) if guard else None,
                    bpdu_guard=bpdu_guard,
                    bpdu_filter=bpdu_filter,
                    portfast=port_fast,
                    uplink_fast=uplink_fast,
                    bpdu_guard_port_shutdown=bpdu_guard_port_shutdown,
                    cost=cost,
                    port_priority=port_priority,
                    stp_enabled=stp_enabled,
                )
                add_msg_to_list(result, get_success_msg(request))
            except Exception as err:
                import traceback
                print(traceback.format_exc())
                add_msg_to_list(result, get_failure_msg(err, request))
                http_status = http_status and False
        if request.method == "DELETE":
            device_ip = req_data.get("mgt_ip", "")
            if not device_ip:
                return Response(
                    {"status": "Required field device mgt_ip not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if_name = req_data.get("if_name", None)
            try:
                delete_stp_port_member(device_ip=device_ip, if_name=if_name)
                add_msg_to_list(result, get_success_msg(request))
            except Exception as err:
                add_msg_to_list(result, get_failure_msg(err, request))
                http_status = http_status and False
    return Response(
        {"result": result},
        status=(status.HTTP_200_OK if http_status else status.HTTP_500_INTERNAL_SERVER_ERROR),
    )