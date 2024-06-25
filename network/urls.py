""" Network URL Configuration """

from django.urls import re_path, path

from . import views
from . import vlan, interface, port_chnl, mclag, bgp, port_group

urlpatterns = [
    re_path("del_db", views.delete_db, name="del_db"),
    re_path("discover", views.discover, name="discover"),
    re_path("devices", views.device_list, name="device"),
    re_path("interface_pg", interface.interface_pg, name="interface_pg"),
    path("interface_resync", interface.interface_resync, name="interface_resync"),
    re_path(
        "interfaces", interface.device_interfaces_list, name="device_interface_list"
    ),
    re_path("port_chnls", port_chnl.device_port_chnl_list, name="device_port_chnl"),
    path("port_chnl_ip_remove", port_chnl.remove_port_channel_ip_address, name="port_channel_ip_remove"),
    path("port_chnl_vlan_member_remove", port_chnl.remove_port_channel_member_vlan, name="port_chnl_vlan_member_remove"),
    re_path("mclags", mclag.device_mclag_list, name="device_mclag_list"),
    re_path("bgp", bgp.device_bgp_global, name="bgp_global"),
    re_path("nbrs", bgp.bgp_nbr_config, name="bgp_nbr"),
    re_path("group_mem", port_group.port_group_members, name="port_group_members"),
    re_path("groups", port_group.port_groups, name="port_groups"),
    re_path("gateway_mac", mclag.mclag_gateway_mac, name="mclag_gateway_mac"),
    re_path("vlan_ip_remove", vlan.remove_vlan_ip_address, name="vlan_ip_remove"),
    re_path("vlan_mem_delete", vlan.vlan_mem_config, name="vlan_mem_delete"),
    re_path("vlan", vlan.vlan_config, name="vlan_config"),
]
