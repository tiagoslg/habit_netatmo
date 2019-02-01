from django.urls import path
from .views import *

urlpatterns = [
    path(r'', DashboardView.as_view(), name='dashboard'),
]
