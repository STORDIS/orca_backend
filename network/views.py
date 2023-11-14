from django.http import JsonResponse
from rest_framework.decorators import api_view
from orca_nw_lib.device import get_device_details
from orca_nw_lib.discovery import discover_all


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
