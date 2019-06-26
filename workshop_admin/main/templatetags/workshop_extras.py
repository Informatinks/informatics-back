from django import template
from django.conf import settings
from main.models import WorkshopConnectionStatus

register = template.Library()


@register.filter(name='public_link')
def public_link(workshop):
    return f'{settings.MAIN_APP_URL}/workshops/{workshop.id}/join?token={workshop.access_token}'


@register.filter(name='humazine_wsconnection_status')
def humazine_wsconnection_status(status):
    return WorkshopConnectionStatus(status).name
