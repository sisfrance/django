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
    path(r'projet/<str:id>/',views.details_projet),
    path(r'projets/',views.projets),
    path(r'projets/page/',views.projets_page),
    path(r'projets/sort/',views.projets_sort),
    path(r'projets/nb/',views.projets_nb),
    path(r'client/<str:id>/',views.details_client),
    path(r'clients/',views.clients),
    path(r'clients/page/',views.clients_page),
    path(r'clients/sort/',views.clients_sort),
    path(r'clients/nb/',views.clients_nb),
    path(r'currents/',views.currents),
    path('admin/', admin.site.urls),
    path(r'download/',views.download),
    path(r'kanban/search',views.accueil_search),
    #path(r'nom_domaines/',views.noms_domaines),
    path(r'travail/',views.temps_passe),
    path(r'projets/search/',views.projets_search),
    path(r'clients/search/',views.clients_search),
    #path(r'accueil/search/',views.accueil_search),
    path(r'add/',views.add),
    path(r'edit/',views.edit),
    path(r'save/',views.save),
]
