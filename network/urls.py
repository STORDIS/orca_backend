""" Network URL Configuration """

from django.urls import re_path, path

from . import views, stp_vlan, stp_port, vlan, interface, port_chnl, mclag, bgp, port_group, stp, ip_polling

urlpatterns = [
    path("ip/range", ip_polling.ip_range, name="ip_range"),
    path("ip/availability", ip_polling.ip_availability, name="ip_availability"),
    path("ip/available", ip_polling.get_available_ip, name="available_ips"),
    path("stp", stp.stp_global_config, name="stp_config"),
    path("stp_delete_disabled_vlans", stp.delete_disabled_vlans, name="stp_delete_disabled_vlans"),
    path("stp_port", stp_port.stp_port_config, name="stp_port"),
    path("stp_discovery", stp_port.stp_discovery, name="stp_discovery"),
    path("stp_vlan", stp_vlan.stp_vlan_config, name="stp_vlan_config"),
    path("breakout", interface.interface_breakout, name="breakout"),
    re_path("del_db", views.delete_db, name="del_db"),
    # path("discover", views.discover, name="discover"),
    path("discover/feature", views.discover_by_feature, name="discover_by_feature"),
    path("discover/schedule", views.discover_scheduler, name="discover_scheduler"),
    re_path("devices", views.device_list, name="device"),
    path("subinterface", interface.interface_subinterface_config, name="subinterface"),
    re_path("interface_pg", interface.interface_pg, name="interface_pg"),
    path("interface_resync", interface.interface_resync, name="interface_resync"),
    re_path(
        "interfaces", interface.device_interfaces_list, name="device_interface_list"
    ),
    re_path("port_chnls", port_chnl.device_port_chnl_list, name="device_port_chnl"),
    path(
        "port_chnl_ip_remove",
        port_chnl.remove_port_channel_ip_address,
        name="port_channel_ip_remove",
    ),
    path(
        "port_channel_member_vlan",
        port_chnl.port_channel_member_vlan,
        name="port_channel_member_vlan",
    ),
    path(
        "port_chnl_vlan_member_remove_all",
        port_chnl.remove_all_port_channel_member_vlan,
        name="port_chnl_vlan_member_remove_all",
    ),
    path(
        "port_chnl_mem_ethernet",
        port_chnl.port_chnl_mem_ethernet,
        name="port_chnl_mem_ethernet",
    ),
    re_path("mclags", mclag.device_mclag_list, name="device_mclag_list"),
    path(
        "delete_mclag_members", mclag.delete_mclag_members, name="delete_mclag_members"
    ),
    re_path(
        "config_mclag_fast_convergence",
        mclag.config_mclag_fast_convergence,
        name="config_mclag_fast_convergence",
    ),
    path("bgp_af", bgp.bgp_af, name="bgp_af"),
    path("bgp_af_network", bgp.bgp_af_network, name="bgp_af_network"),
    path("bgp_af_aggregate_addr", bgp.bgp_af_aggregate_addr, name="bgp_af_aggregate_addr"),
    path("nbrs_af", bgp.bgp_neighbor_af, name="bgp_nbr_af"),
    path("nbrs", bgp.bgp_nbr_config, name="bgp_nbr"),
    path("nbrs_remote_bgp", bgp.bgp_neighbor_remote_bgp, name="bgp_nbr_remote_bgp"),
    path("nbrs_local_bgp", bgp.bgp_neighbor_local_bgp, name="bgp_nbr_local_bgp"),
    path("nbrs_subinterface", bgp.bgp_neighbor_sub_interface, name="bgp_nbr_subinterface"),
    re_path("bgp", bgp.device_bgp_global, name="bgp_global"),
    re_path(
        "group_from_intfc",
        port_group.port_group_from_intfc_name,
        name="group_from_intfc",
    ),
    re_path("group_mem", port_group.port_group_members, name="port_group_members"),
    re_path("groups", port_group.port_groups, name="port_groups"),
    re_path("gateway_mac", mclag.mclag_gateway_mac, name="mclag_gateway_mac"),
    re_path("vlan_ip_remove", vlan.remove_vlan_ip_address, name="vlan_ip_remove"),
    re_path("vlan_mem_delete", vlan.vlan_mem_config, name="vlan_mem_delete"),
    re_path("vlan", vlan.vlan_config, name="vlan_config"),
]
