from django.urls import path

from . import views
from . import vlan, interface, port_chnl, mclag, bgp, port_group

urlpatterns = [
    path("discover", views.discover, name="discover"),
    path("devices", views.device_list, name="device_list"),
    path("devices", views.device_list, name="device"),
    path("interfaces", interface.device_interfaces_list, name="device_interface_list"),
    path("port_chnls", port_chnl.device_port_chnl_list, name="device_port_chnl"),
    path("mclags", mclag.device_mclag_list, name="device_mclag_list"),
    path("bgp", bgp.device_bgp_global, name="bgp_global"),
    path("bgp_nbrs", bgp.bgp_nbr_config, name="bgp_nbr"),
    path("port_groups", port_group.port_groups, name="port_groups"),
    path("gateway_mac", mclag.mclag_gateway_mac, name="mclag_gateway_mac"),
    path("vlan", vlan.vlan_config, name="vlan_config"),
]
