""" Network URL Configuration """
from django.urls import re_path

from . import views
from . import vlan, interface, port_chnl, mclag, bgp, port_group

urlpatterns = [
    re_path("discover", views.discover, name="discover"),
    re_path("devices", views.device_list, name="device"),
    re_path("interfaces", interface.device_interfaces_list, name="device_interface_list"),
    re_path("port_chnls", port_chnl.device_port_chnl_list, name="device_port_chnl"),
    re_path("mclags", mclag.device_mclag_list, name="device_mclag_list"),
    re_path("bgp", bgp.device_bgp_global, name="bgp_global"),
    re_path("nbrs", bgp.bgp_nbr_config, name="bgp_nbr"),
    re_path("groups", port_group.port_groups, name="port_groups"),
    re_path("gateway_mac", mclag.mclag_gateway_mac, name="mclag_gateway_mac"),
    re_path("vlan", vlan.vlan_config, name="vlan_config"),
]
