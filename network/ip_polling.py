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
            else Response(status=status.HTTP_204_NO_CONTENT)
        )
    req_data_list = request.data if isinstance(request.data, list) else [request.data]
    if request.method == "PUT":
        for req_data in req_data_list:
            try:
                ip_range = req_data.get("range")
                IPRange.add_ip_range(range=ip_range)
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
                IPRange.delete_ip_range(ip_range)
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
        range = request.GET.get("range")
        if range is None:
            ip_availability_list = IPAvailability.objects.all()
        else:
            ip_range = IPRange.objects.get(range=range)
            ip_availability_list = IPAvailability.objects.filter(range=ip_range)
        for ip in ip_availability_list:
            result.append(
                {
                    "ip": ip.ip, 
                    "used_in": ip.used_in,
                    "range": [ip_range.range for ip_range in ip.range.all()]
                }
            )
        return (
            Response(result, status=status.HTTP_200_OK)
            if result
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
    

@api_view(["GET"])
@log_request
def get_available_ip(request):
    if request.method == "GET":
        try:
            range = request.GET.get("range")
            if range is None:
                ips_available_list = IPAvailability.objects.filter(used_in__isnull=True)
            else:
                ip_range = IPRange.objects.get(range=range)
                ips_available_list = IPAvailability.objects.filter(range=ip_range, used_in__isnull=True)
            return Response([ip.ip for ip in ips_available_list], status=status.HTTP_200_OK)
        except Exception as e:
            _logger.error(e)
            return Response({"status": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)