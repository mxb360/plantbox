"""plantBoxServer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
#from django.contrib import admin
from app import views

urlpatterns = [
    #url(r'^admin/', admin.site.urls),
    url(r'^index$', views.tcs),
    url(r'^web/(.+)$', views.website),
    url(r'^admin/(.+)$', views.web_admin),
    url(r'^py_admin/(.+)$', views.py_admin),
    url(r'^app/connect/(.+)$', views.user_connect_by_app),
    url(r'^app/(.+)/(.+)/(.+)$', views.app_cmd),
    url(r'^wx/(.+)/(.+)/(.+)$', views.wx_cmd),
    url(r'^web/(.+)/(.+)/(.+)$', views.web_cmd),
    url(r'^stream/(.+)$', views.stream),
    url(r'^$', views.index),
    url(r'^web_connect/(.+)$', views.user_connect_by_web),
    url(r'^app/download$', views.app_download),
]
