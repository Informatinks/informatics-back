from collections import namedtuple

from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from main.models import WorkshopConnection, WorkshopConnectionStatus

Status = namedtuple('Status', ['title', 'id'])


class WorkshopConnectionMassUpdateAdmin(View):
    """View for bulk changing WorkshopConnection statuses.

    Should be used from Django admin panel.
    """

    def get(self, request, *args, **kwargs):
        try:
            content_type = int(request.GET.get('ct'))
            ids = [int(id) for id in request.GET.getlist('id')]
        except (TypeError, ValueError):
            return HttpResponseBadRequest()

        # Find objects of requested type
        try:
            ct = ContentType.objects.get(id=content_type, app_label='main')
        except ContentType.DoesNotExist:
            return HttpResponseBadRequest()

        objs = WorkshopConnection.objects.prefetch_related('user', 'workshop').filter(pk__in=ids)

        return render(request, 'admin/main/workshop/change_status.html', {
            'objects': objs,
            'statuses': [Status(s.name, s.value) for s in WorkshopConnectionStatus]
        })

    def post(self, request, *args, **kwargs):
        try:
            status = int(request.POST.get('status'))
            object_ids = [int(i) for i in request.POST.getlist('object_id')]
        except ValueError:
            return HttpResponseBadRequest()

        WorkshopConnection.objects.filter(id__in=object_ids).update(status=status)

        messages.add_message(request, messages.INFO, 'Статус заявок успешно обновлен!')
        return redirect(reverse('admin:main_workshopconnection_changelist'))
