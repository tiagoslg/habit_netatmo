from django.urls import path
from .views import *

urlpatterns = [
    path(r'', DashboardView.as_view(), name='dashboard'),
    path(r'signin/', SigninView.as_view(), name='dashboard'),
]
