from django import template
from django.conf import settings

register = template.Library()


@register.filter(name='public_link')
def public_link(workshop):
    return f'{settings.MAIN_APP_URL}/workshops/{workshop.id}/join?token={workshop.access_token}'
