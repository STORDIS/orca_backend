from django.urls import path, re_path

from . import views
from . import vlan,interface,port_chnl,mclag

urlpatterns = [
    path("discover", views.discover, name="discover"),
    path("devices", views.device_list, name="device_list"),
    re_path('devices', views.device_list,name="device"),
    re_path("interfaces", interface.device_interfaces_list, name="device_interface_list"),
    re_path("port_chnls", port_chnl.device_port_chnl_list, name="device_port_chnl"),
    re_path("mclags", mclag.device_mclag_list, name="device_mclag_list"),
    re_path("bgp", views.device_bgp_global, name="bgp_global"),
    re_path("port_groups", views.port_groups, name="port_groups"),
    re_path("gateway_mac", mclag.mclag_gateway_mac, name="mclag_gateway_mac"),
    re_path("vlan", vlan.vlan_config, name="vlan_config")
    ]
