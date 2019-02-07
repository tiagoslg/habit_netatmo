from django.urls import path
from .views import *

urlpatterns = [
    path(r'', DashboardView.as_view(), name='dashboard'),
    path(r'signin/', SigninView.as_view(), name='signin'),
    path(r'get_temperature/<str:device_id>/', GetThermostatTemperature.as_view(), name='get_temperature'),
    path(r'get_station/<str:device_id>/', GetStationData.as_view(), name='get_station'),
    path(r'refresh_access_token/', RefreshAccessToken.as_view(), name='refresh_access_token')
]
