import os
from django.shortcuts import render

from django.http import HttpResponse, JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from orca_nw_lib.device import getDeviceDetailsFromGraph
from orca_nw_lib.interfaces import getInterfacesDetailsFromGraph, config_interface
from orca_nw_lib.port_chnl import getPortChnlDetailsFromGraph
from orca_nw_lib.mclag import getMCLAGsFromGraph
from orca_nw_lib.discovery import discover_all

@api_view(['GET',])
def discover(request):
    if request.method == 'GET':
        data=discover_all()
        if data:
            return JsonResponse({"result":"Success"}, safe=False)
        else:
            return JsonResponse({"result":"Fail"}, safe=False)

@api_view(['GET',])
def device_list(request):
    if request.method == 'GET':
        data=getDeviceDetailsFromGraph(request.GET.get('mgt_ip',''))
        return JsonResponse(data, safe=False)
    
@api_view(['GET','PUT'])
def device_interfaces_list(request):
    device_ip=request.GET.get('mgt_ip','')
    if not device_ip :
        return Response({"status": "Required field device mgt_ip not found."},
                                    status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'GET':
        intfc_name=request.GET.get('intfc_name','')
        data=getInterfacesDetailsFromGraph(device_ip,intfc_name)
        return JsonResponse(data, safe=False)
    elif request.method == 'PUT':
        req_data=request.data
        if req_data.get('name') is None:
            return Response({"status": "Required field device mgt_ip not found."},
                                    status=status.HTTP_400_BAD_REQUEST)
        if config_interface(device_ip=device_ip,intfc_name=req_data.get('name'),enable=req_data.get('enabled'),
                         mtu=req_data.get('mtu'),loopback=req_data.get('loopback-mode'),description=req_data.get('description'),
                         speed=req_data.get('port-speed')) is None:
            return Response({"status": "Error occured while applying config."},
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET',])
def device_port_chnl_list(request):
    if request.method == 'GET':
        device_ip=request.GET.get('mgt_ip','')
        if not device_ip :
            return Response({"status": "Required field device mgt_ip not found."},
                                        status=status.HTTP_400_BAD_REQUEST)
        port_chnl_name=request.GET.get('chnl_name','')
        data=getPortChnlDetailsFromGraph(device_ip,port_chnl_name)
        return JsonResponse(data, safe=False)
    
@api_view(['GET',])
def device_mclag_list(request):
    if request.method == 'GET':
        device_ip=request.GET.get('mgt_ip','')
        if not device_ip :
            return Response({"status": "Required field device mgt_ip not found."},
                                        status=status.HTTP_400_BAD_REQUEST)
        domain_id=request.GET.get('domain_id','')
        data=getMCLAGsFromGraph(device_ip,domain_id)
        return JsonResponse(data, safe=False)