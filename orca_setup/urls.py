from django.urls import path

from orca_setup import setup, views

urlpatterns = [
    path("switch_image", setup.switch_sonic_image, name="switch_image"),
    path("install_image", setup.install_image, name="install_image"),
    path("celery", views.celery_task, name="celery_task"),
]