from django.urls import re_path, path
from fileserver import views

urlpatterns = [
    re_path(r"^download/(?P<filepath>.*)/?$", views.download_file, name="download_file"),
    path("ztp", views.host_ztp_files, name="host_ztp_files"),
    path("ztp/rename", views.rename_ztp_file, name="rename_ztp_file"),
    path("dhcp/credentials", views.dhcp_auth, name="dhcp_credentials"),
    path("dhcp/config", views.dhcp_config, name="dhcp_config"),
    path("dhcp/backups", views.dhcp_backup, name="dhcp_backups"),
    path("dhcp/list", views.get_dhcp_device, name="dhcp_list"),
    path("templates", views.get_templates, name="templates"),
]
