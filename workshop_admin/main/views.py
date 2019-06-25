from collections import namedtuple

from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.urls import reverse
from main.models import WorkshopConnection, WorkshopConnectionStatus

Status = namedtuple('Status', ['title', 'id'])


def change_conn_status(request):
    """View for bulk changing WorkshopConnection statuses.

    Should be used from Django admin panel.
    """
    if request.method == 'POST':
        # Validate payload params
        params = {
            'object_ids': request.POST.get('object_ids'),
            'status': request.POST.get('status'),
        }

        if params.get('object_ids') is None or params.get('status') is None:
            return HttpResponseBadRequest()

        # Cast POST params values
        try:
            ids = [int(id) for id in params.get('object_ids').split(',')]
            status = int(params.get('status'))
        except (TypeError, ValueError):
            return HttpResponseBadRequest()

        # Bulk update coonections
        WorkshopConnection.objects.filter(id__in=ids).update(status=status)

        messages.add_message(request, messages.INFO, 'Статус заявок успешно обновлен!')
        return redirect(reverse('admin:main_workshopconnection_changelist'))
    else:
        # Validate payload params
        params = {
            'content_type': request.GET.get('ct'),
            'object_ids': request.GET.get('ids'),
        }

        if params.get('content_type') is None or params.get('object_ids') is None:
            return HttpResponseBadRequest()

        # Cast GET params values
        try:
            ids = [int(id) for id in params.get('object_ids').split(',')]
        except (TypeError, ValueError):
            return HttpResponseBadRequest()

        # Find objects of requested type
        ct = ContentType.objects.get(id=params.get('content_type'), app_label='main')
        objs = WorkshopConnection.objects.filter(pk__in=ids)

        return render(request, 'admin/main/workshop/change_status.html', {
            'objects': objs,
            # Pepare data for rendering in view
            'obj_ids': ','.join([str(o.id) for o in objs]),
            'statuses': [Status(s.name, s.value) for s in WorkshopConnectionStatus]
        })
