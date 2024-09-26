"""
URL configuration for orca_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from orca_backend.settings import INSTALLED_APPS

urlpatterns = [
    path("", include("network.urls")),
    path("admin/", admin.site.urls),
    path("auth/", include("authentication.urls")),
    path("logs/", include("log_manager.urls")),
    path("state/", include("state_manager.urls")),
]

if 'orcask' in INSTALLED_APPS:
    urlpatterns += [
        path("orcask/", include("orcask.urls")),
    ]