from collections import namedtuple

from django import forms
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from main.models import WorkshopConnection, WorkshopConnectionStatus, WORKSHOP_CONNECTION_STATUS_CHOICES, Workshop
from moodle.models import MoodleUser

Status = namedtuple('Status', ['title', 'id'])


class MassInviteForm(forms.Form):
    users_file = forms.FileField(label='Список учеников для инвайта',
                                 required=True,
                                 help_text='Файл должен список ID или логинов пользователей по одному на каждой строке')
    status = forms.ChoiceField(choices=WORKSHOP_CONNECTION_STATUS_CHOICES,
                               required=True,
                               label='В каком статусе записать учеников?')


class WorkshopConnectionMassUpdateAdmin(LoginRequiredMixin, View):
    """View for bulk changing WorkshopConnection statuses.

    Should be used from Django admin panel.
    """

    @property
    def login_url(self):
        return reverse('admin:login')

    def get(self, request, *args, **kwargs):
        try:
            ids = [int(id) for id in request.GET.getlist('id')]
        except (TypeError, ValueError):
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


class WorkshopMassInviteAdmin(LoginRequiredMixin, View):
    @property
    def login_url(self):
        return reverse('admin:login')

    def _render_form_response(self, form, workshop=None):
        """Generic method for response with form.

        Can render form with valid workshop or response for invalid workshop requests.
        """
        return render(self.request, 'admin/main/workshop/mass_invite.html', {
            'form': form,
            'workshop': workshop
        })

    def get(self, request, *args, **kwargs):
        workshop_id = request.GET.get('id')
        form = MassInviteForm()

        # If user requested invalid workshop,
        # safe failback to form with error
        try:
            workshop = Workshop.objects.get(pk=workshop_id)
        except Workshop.DoesNotExist:
            messages.add_message(request, messages.ERROR,
                                 'Запрошенный сбор с таким ID не найден. '
                                 'Попробуйте начать процесс массового добавления заново со страницы сбора.')
            return self._render_form_response(form)

        return self._render_form_response(form, workshop)

    def post(self, request, *args, **kwargs):
        workshop_id = request.GET.get('id')
        form = MassInviteForm(request.POST, request.FILES)

        # Find requested workshop
        try:
            workshop = Workshop.objects.get(pk=workshop_id)
        except:
            messages.add_message(request, messages.ERROR,
                                 'Запрошенный сборк с таким ID не найден. '
                                 'Попробуйте начать процесс массового добавления заново со страницы сбора.')
            return self._render_form_response(form)

        if not form.is_valid():
            return self._render_form_response(form, workshop)

        # Decode request payload
        workshop_id = request.GET.get('id')
        status = form.cleaned_data.get('status')
        users_file = form.cleaned_data.get('users_file')

        # Clear provided users features
        # One feature per line
        users_featues = [
            line.decode('utf-8').rstrip('\n,')
            for line in users_file.readlines()
        ]

        # Determine, which feature is supplied
        try:
            users_featues = [int(feat) for feat in users_featues]
            feature_name = 'id'
        except ValueError:
            feature_name = 'username'

        # Create connection for each user
        for feature_value in users_featues:
            try:
                # Find user with determined feature
                user = MoodleUser.objects.get(**{feature_name: feature_value})

                # Safe create connection to avoid race conditions
                workshop_conn = WorkshopConnection.objects.get_or_create(user=user,
                                                                         workshop=workshop,
                                                                         status=status)
                messages.add_message(request, messages.SUCCESS,
                                     f'Пользователь «{feature_value}» был успешно записан на воркшоп')
            except MoodleUser.DoesNotExist:
                # Can't find user by determined feature
                messages.add_message(request, messages.ERROR,
                                     f'Пользователь «{feature_value}» не был найден в базе!')
            except IntegrityError:
                # Get_or_create returned error, which usually means
                # there's another connection for this workshop
                WorkshopConnection.objects.filter(user=user, workshop=workshop).update(status=status)
                messages.add_message(request, messages.WARNING,
                                     f'Для пользователя «{feature_value}» обновлена заявка на этот сбор.')

        return redirect(reverse('admin:main_workshopconnection_changelist'))
