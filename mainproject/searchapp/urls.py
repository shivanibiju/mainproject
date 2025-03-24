from django.contrib import admin
from django.urls import path, include
from . import views
from .views import register_view
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('styles/', views.styles, name='styles'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('search/', views.search_view, name='search'),
    path('normal_search',views.normal_search_view, name='normal_search'),
    path('normal_search/results/', views.normal_search_results, name='normal_search_results'),
    path('t_register/', views.t_register_view, name='t_register'),
    path('t_login/', views.t_login_view, name='t_login'),
    path('t_home/', views.t_home, name='t_home'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)