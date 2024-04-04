from django.urls import path
from log_manager import views


urlpatterns = [
    path("all/<int:page>", views.get_logs),
]