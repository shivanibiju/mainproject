"""
URL configuration for mainproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path, include
from . import views
from .views import register_view

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('search/', views.search_view, name='search'),
    path('normal_search',views.normal_search_view, name='normal_search'),
    path('normal_search/results/', views.normal_search_results, name='normal_search_results'),
    path('t_register/', views.t_register_view, name='t_register'),
    path('t_login/', views.t_login_view, name='t_login'),
    path('t_home/', views.t_home, name='t_home'),
    path('skill_profile/edit/<int:id>/', views.edit_skill_profile, name='edit_skill_profile'),
    path('skill_profile/delete/<int:id>/', views.delete_skill_profile, name='delete_skill_profile'),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)