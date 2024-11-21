from django.urls import re_path, path
from fileserver import views

urlpatterns = [
    re_path(r"^download/(.+)/$", views.download_file, name="download_file"),
    path("ztp", views.host_ztp_files, name="host_ztp_files"),
    path("dhcp/credentials", views.dhcp_credentials, name="dhcp_credentials"),
    path("dhcp/config", views.dhcp_config, name="dhcp_config"),
    path("dhcp/backups", views.dhcp_backup, name="dhcp_backups"),
    path("dhcp/list", views.get_dhcp_device, name="dhcp_list"),
]
