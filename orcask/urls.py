from django.urls import path

from orcask import views

urlpatterns = [
    path("completions", views.completions_view),
]
