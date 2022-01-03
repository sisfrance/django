"""runtastic URL Configuration

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
from django.urls import include, path
from runtastic.dashboard import views
from django.conf import settings

urlpatterns = [
    path(r'',views.index),
    path(r'import/',views.import_file),
    path(r'list/',views.sessions),
    path(r'sessions/page/',views.page),
    path(r'search/',views.search),
    path(r'stats/',views.stats),
    path(r'dashboard/nb/',views.nb),
    path(r'details/<str:id>/',views.details),
    path(r'filtresportsannee/',views.filtresportsannee),
    path(r'filtresportsmois/',views.filtresportsmois),
    path(r'filtrestats/',views.filtrestats),
    path(r'download/',views.download),
    path('admin/', admin.site.urls),
    
]
