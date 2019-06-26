from django.urls import path

from .views import WorkshopConnectionMassUpdateAdmin 

urlpatterns = [
    path('change_status', WorkshopConnectionMassUpdateAdmin.as_view(), name='change_wsconn_status'),
]
