from django import template
from django.conf import settings
from main.models import WORKSHOP_CONNECTION_STATUS_CHOICES

register = template.Library()


@register.filter(name='public_link')
def public_link(workshop):
    return f'{settings.MAIN_APP_URL}/workshops/{workshop.id}/join?token={workshop.access_token}'


@register.filter(name='humazine_wsconnection_status')
def humazine_wsconnection_status(status):
    a = [wc_status for wc_status in WORKSHOP_CONNECTION_STATUS_CHOICES if wc_status[0] == status]
    return a and a[0] or None
