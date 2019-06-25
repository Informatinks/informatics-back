from django.urls import path

from .views import change_conn_status

urlpatterns = [
    path('change_status', change_conn_status, name='change_conn_status'),
]
