from django.urls import path
from .views import *

urlpatterns = [
    path(r'', DashboardView.as_view(), name='dashboard'),
    path(r'get_temperature/<str:device_id>/', GetThermostatTemperature.as_view(), name='get_temperature'),
    path(r'get_station/<str:device_id>/', GetStationData.as_view(), name='get_station'),
    path(r'refresh_access_token/', RefreshAccessToken.as_view(), name='refresh_access_token'),
    path(r'get_camera_con_status/<str:device_id>/', GetCameraConnectionStatus.as_view(), name='get_station'),
    path(r'webhook_client/', webhook, name='webhook'),
    path(r'webhook_list/', WebHooksView.as_view(), name='webhook_list'),
]
