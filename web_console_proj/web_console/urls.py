from django.urls import path
from . import views

urlpatterns = [
    path('', views.device_list, name='device_list'),
    path('device/<str:device_id>/', views.device_detail, name='device_detail'),
    path('device/<str:device_id>/set_status/', views.set_device_status, name='set_device_status'),
    path('api/device/<str:device_id>/control/', views.api_control_device, name='api_control_device'),
] 