from django.urls import path
from state_manager import views

urlpatterns = [
    path("<device_ip>", views.get_orca_state, name="orca_state"),
]
