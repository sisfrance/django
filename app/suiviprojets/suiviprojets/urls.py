"""suiviprojets URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.urls import path
from suiviprojets.dashboard import views
from django.conf import settings

urlpatterns = [
    path(r'',views.index),
    path(r'details/<str:id>/',views.details),
    path(r'projects/',views.projets),
    path(r'projects/page/',views.page),
    path(r'projects/sort/',views.sort),
    path(r'client/<str:id>/',views.details_client),
    path(r'clients/',views.clients),
    path(r'currents/',views.currents),
    path('admin/', admin.site.urls),
    path(r'download/',views.download),
    path(r'search/',views.search),
    path(r'add/',views.add),
    path(r'edit/',views.edit),
    path(r'save/',views.save),
]
