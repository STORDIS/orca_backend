import ipaddress
from django.forms import model_to_dict
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from log_manager.decorators import log_request
from log_manager.logger import get_backend_logger
from network.models import IPAvailability, IPRange
from network.util import add_msg_to_list, get_failure_msg, get_success_msg


_logger = get_backend_logger()


@api_view(["PUT", "GET", "DELETE"])
@log_request
def ip_range(request):
    result = []
    http_status = True
    if request.method == "GET":
        data = IPRange.objects.all()
        return (
            Response([model_to_dict(ip_range) for ip_range in data], status=status.HTTP_200_OK)
            if data
            else Response({}, status=status.HTTP_204_NO_CONTENT)
        )
    req_data_list = request.data if isinstance(request.data, list) else [request.data]
    if request.method == "PUT":
        for req_data in req_data_list:
            try:
                ip_range = req_data.get("range")
                IPRange.objects.update_or_create(range=ip_range)
                ips_in_range = get_ips_in_range(ip_range)
                for ip in ips_in_range:
                    IPAvailability.create_if_not_exist(ip)
                add_msg_to_list(result, get_success_msg(request))
            except Exception as e:
                import traceback
                print(traceback.format_exc())
                _logger.error(e)
                http_status = False
                add_msg_to_list(result, get_failure_msg(e, request))
                
    if request.method == "DELETE":
        for req_data in req_data_list:
            try:
                ip_range = req_data.get("range")
                IPRange.objects.filter(range=ip_range).delete()
                ips_in_range = get_ips_in_range(ip_range)
                for ip in ips_in_range:
                    IPAvailability.delete_if_not_used(ip=ip)
                add_msg_to_list(result, get_success_msg(request))
            except Exception as e:
                _logger.error(e)
                http_status = False
                add_msg_to_list(result, get_failure_msg(e, request))
    return Response(
        {"result": result},
        status=(status.HTTP_200_OK if http_status else status.HTTP_500_INTERNAL_SERVER_ERROR),
    )
    
    
@api_view(["PUT", "GET", "DELETE"])
@log_request
def ip_availability(request):
    result = []
    http_status = True
    if request.method == "GET":
        data = IPAvailability.objects.filter(used_in__isnull=True)
        return (
            Response([model_to_dict(ip_range) for ip_range in data], status=status.HTTP_200_OK)
            if data
            else Response({}, status=status.HTTP_204_NO_CONTENT)
        )
    req_data_list = request.data if isinstance(request.data, list) else [request.data]
    if request.method == "PUT":
        for req_data in req_data_list:
            try:
                ip = req_data.get("ip")
                used_in = req_data.get("used_in")
                if ip is None:
                    _logger.error("Required field ip not found")
                    return Response(
                        {"status": "Required field ip not found"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                if used_in is None:
                    _logger.error("Required field used_in not found")
                    return Response(
                        {"status": "Required field used_in not found"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                item=IPAvailability.objects.get(ip=ip)
                item.used_in = used_in
                item.save()
                add_msg_to_list(result, get_success_msg(request))
            except Exception as e:
                _logger.error(e)
                http_status = False
                add_msg_to_list(result, get_failure_msg(e, request))
    if request.method == "DELETE":
        for req_data in req_data_list:
            try:
                ip = req_data.get("ip")
                if ip is None:
                    _logger.error("Required field ip not found")
                    return Response(
                        {"status": "Required field ip not found"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                item=IPAvailability.objects.get(ip=ip)
                item.used_in = None
                item.save()
                add_msg_to_list(result, get_success_msg(request))
            except Exception as e:
                _logger.error(e)
                http_status = False
                add_msg_to_list(result, get_failure_msg(e, request))
    return Response(
        {"result": result},
        status=(status.HTTP_200_OK if http_status else status.HTTP_500_INTERNAL_SERVER_ERROR),
    )
    

def get_ips_in_range(ip_range):
    if "/" in ip_range:
        return [str(ip) for ip in ipaddress.ip_network(ip_range, strict=True)]
    elif "-" in ip_range:
        ip_split =  ip_range.split("-")
        start = ip_split[0].strip()
        end = ip_split[1].strip()
        start_int = int(ipaddress.ip_address(start).packed.hex(), 16)
        end_int = int(ipaddress.ip_address(end).packed.hex(), 16)
        return [str(ipaddress.ip_address(ip)) for ip in range(start_int, end_int)]
    else:
        raise Exception("Invalid IP Range")