from django.urls import path

from .views import (
    WorkshopConnectionMassUpdateAdmin,
    WorkshopMassInviteAdmin
)

urlpatterns = [
    path('change_status', WorkshopConnectionMassUpdateAdmin.as_view(), name='change_wsconn_status'),
    path('mass_invite', WorkshopMassInviteAdmin.as_view(), name='workshop_mass_invite'),
]
