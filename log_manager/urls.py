from django.urls import include, re_path, path
from oauth2_provider import views as oauth2_views
from log_manager import views


urlpatterns = [
    path("save", views.save_log),
    path("all/<int:page>", views.get_logs),
]