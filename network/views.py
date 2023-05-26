from django.shortcuts import render

from django.http import HttpResponse, JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from orca_nw_lib.device import getDeviceDetailsFromGraph,getDeviceDetails


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

@api_view(['GET', 'POST'])
def device_list(request):
    if request.method == 'GET':
        data=getDeviceDetailsFromGraph()
        return JsonResponse(data, safe=False)
    
    
@api_view(['PUT', 'DELETE'])
def device_detail(request, pk):
    if request.method == 'GET':
        data=getDeviceDetails('10.10.130.13')
        return JsonResponse(data, safe=False)