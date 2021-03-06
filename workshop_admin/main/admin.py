import datetime
from urllib.parse import urlencode

from ajax_select import make_ajax_form
from ajax_select.admin import AjaxSelectAdminTabularInline, AjaxSelectAdmin
from django import forms
from django.contrib import admin
from django.db.models import Q
from django.forms import ModelForm, ValidationError
from django.http import HttpResponseRedirect
from django.urls import reverse
from grappelli.forms import GrappelliSortableHiddenMixin
from moodle.models import Statement, MoodleUser

from .models import (
    WorkshopConnection,
    Workshop,
    ContestConnection,
    Contest,
    WorkshopMonitor,
    WorkshopConnectionStatus,
    Language,
    LanguageContest)


def _get_allowed_workshops_for(user: MoodleUser):
    """Get iterable Workshops queryset,
    which can be edited by provided user.

    Used in WorkshopConnection change form.

    user: MoodleUser, for which we retrieve avialable workshops
    """
    # If provided user is superuser,
    # allow edit all WorkshopConnections
    if user.is_superuser:
        return Workshop.objects.all()

    return Workshop.objects.filter(
        Q(owner=user) |
        Q(connections__status=WorkshopConnectionStatus.PROMOTED.value,
          connections__user=user)) \
        .distinct()


class ScopedWorkshopListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'Сбор'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'workshop'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.

        Uses private _get_allowed_workshops_for() method,
        which is permission-aware. So superusers can view
        all workshops in list filter.
        """
        return _get_allowed_workshops_for(request.user) \
            .values_list('id', 'name')

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        workshop_id = request.GET.get('workshop')
        if not workshop_id:
            return queryset
        return queryset.filter(Q(workshop__id=workshop_id))


class WorkshopConnectionForm(ModelForm):
    """Custom WorkshopConnection form with Workshop relation
    queryset, based on current user permissions.
    """
    workshop = forms.ModelChoiceField(queryset=Workshop.objects.none())

    def __init__(self, *args, **kwargs):
        """Restrict default Workshop relation queryset.
        """
        super(WorkshopConnectionForm, self).__init__(*args, **kwargs)
        self.fields['workshop'].queryset = _get_allowed_workshops_for(self.current_user)


class WorkshopConnectionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'workshop', 'user', 'status',)
    list_filter = ('status', ScopedWorkshopListFilter,)
    form = make_ajax_form(WorkshopConnection, superclass=WorkshopConnectionForm, fieldlist={
        'user': 'moodleuser_lookup'
    })

    def get_form(self, request, obj=None, **kwargs):
        """Inherit get WorkshopConnection form method to store
        current user in Form instance.

        Further it can be used to create custom Workshop queryset,
        based on current user permissions.
        """
        form = super(WorkshopConnectionAdmin, self).get_form(request, **kwargs)
        form.current_user = request.user
        return form

    def get_queryset(self, request):
        """Get connections, which belong to workshop with:
        
        - current user is workshop owner
        - current user has PROMOTED connection
        
        Exclude promoted self connections to prevent
        occasionaly delete self promotion
        """
        qs = super().get_queryset(request)

        # Allow superuser to view all workshop connections
        if request.user.is_superuser:
            return qs

        return qs.filter(Q(workshop__owner=request.user) |
                         Q(workshop__connections__status=WorkshopConnectionStatus.PROMOTED.value,
                           workshop__connections__user=request.user)) \
            .exclude(user=request.user,
                     status=WorkshopConnectionStatus.PROMOTED.value) \
            .distinct()

    def change_status(self, request, queryset):
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)

        # Build query params.
        # Stage as param sequesce, e.g. id=1&id=2&...
        query_params = urlencode({'id': selected}, doseq=True)

        return HttpResponseRedirect('{0}?{1}'.format(
            reverse('change_wsconn_status'),
            query_params)
        )

    change_status.short_description = "Принять или отклонить заявки на сбор"
    change_list_template = "admin/change_list_filter_sidebar.html"
    actions = ['change_status']


class ContestConnectionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'contest', 'user',)
    form = make_ajax_form(ContestConnection, {
        'user': 'moodleuser_lookup'
    })


class LanguageAdminInline(admin.TabularInline):
    model = LanguageContest
    extra = 0  # Don't render default empty formsest


class ContestForm(ModelForm):
    def clean(self):
        """Formset validators on create and update Contest object.

        First we invoke fields auto-validators with `clean()` method.
        Then run our ones with additional logic.
        """
        cleaned_data = super().clean()

        # Contest can be virtual only if virtual duration is supplied.
        is_virtual = cleaned_data.get('is_virtual')
        virtual_duration = cleaned_data.get('virtual_duration')

        if is_virtual and not virtual_duration:
            raise ValidationError(
                'Нельзя сделать контест виртуальным, не указав его длительность. '
                'Укажите длительность в поле "Virtual duration"'
            )


class ContestAdmin(AjaxSelectAdmin):
    readonly_fields = ('author', 'created_at',)
    list_display = ('__str__', 'workshop', 'is_virtual',)
    inlines = (LanguageAdminInline,)
    form = make_ajax_form(Contest, superclass=ContestForm, fieldlist={
        'statement': 'statement_lookup'
    })

    @classmethod
    def add_default_fields(cls, request, obj: Contest):
        obj.author_id = request.user.pk
        obj.created_at = datetime.datetime.utcnow()

    def save_model(self, request, obj: Contest, form, change):
        self.add_default_fields(request, obj)
        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        return ['author', 'created_at']


class ContestAdminInline(GrappelliSortableHiddenMixin, AjaxSelectAdminTabularInline):
    model = Contest
    template = 'admin/main/workshop/edit_inline/tabular.html'
    ordering = ('position',)
    exclude = ('author', 'created_at',)
    sortable_field_name = 'position'
    extra = 0  # Don't render default empty formsest    
    form = make_ajax_form(Contest, superclass=ContestForm, fieldlist={
        'statement': 'statement_lookup'
    })


class MonitorAdminInline(admin.TabularInline):
    model = WorkshopMonitor


class WorkshopAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'status', 'visibility', 'owner')
    readonly_fields = ('owner',)
    inlines = (ContestAdminInline,
               MonitorAdminInline)

    form = make_ajax_form(Workshop, fieldlist={
        'owner': 'moodleuser_lookup'
    })

    def get_queryset(self, request):
        qs = super(WorkshopAdmin, self).get_queryset(request)

        # Allow superuser to view all workshops
        if request.user.is_superuser:
            return qs

        return qs.filter(Q(owner=request.user) |
                         Q(connections__user=request.user,
                           connections__status=WorkshopConnectionStatus.PROMOTED.value)) \
            .distinct()

    def is_new_object_in_form_creating(self, form):
        data = form.cleaned_data
        return data and not data.get('id') and not data.get('DELETE')

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            # Set current user as workshop owner
            obj.owner = request.user
            super().save_model(request, obj, form, change)

            obj.add_connection(request.user)
            return

        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        super().save_formset(request, form, formset, change)
        for idx, f in enumerate(formset.forms):
            if not self.is_new_object_in_form_creating(f):
                continue
            obj = f.instance
            ContestAdmin.add_default_fields(request, obj)
            obj.save()


class WorkshopMonitorAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'workshop', 'type', 'user_visibility',)
    pass


admin.site.register(Contest, ContestAdmin)
admin.site.register(Workshop, WorkshopAdmin)
admin.site.register(WorkshopMonitor, WorkshopMonitorAdmin)
admin.site.register(WorkshopConnection, WorkshopConnectionAdmin)
admin.site.register(ContestConnection, ContestConnectionAdmin)
admin.site.register(Statement)
admin.site.register(Language)
