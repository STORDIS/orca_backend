from django.urls import path
from log_manager import views

urlpatterns = [
    path("all/<int:page>", views.get_logs, name="logs"),
    path("delete", views.delete_logs, name="delete_logs"),
]
