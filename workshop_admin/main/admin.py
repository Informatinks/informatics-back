import datetime
from urllib.parse import urlencode

from ajax_select import make_ajax_form
from ajax_select.admin import AjaxSelectAdminTabularInline, AjaxSelectAdmin
from django.contrib import admin
from django.forms import ModelForm, ValidationError
from django.http import HttpResponseRedirect
from django.urls import reverse
from grappelli.forms import GrappelliSortableHiddenMixin
from moodle.models import Statement

from .models import WorkshopConnection, Workshop, ContestConnection, Contest, WorkshopMonitor


@admin.register(WorkshopConnection)
class WorkshopConnectionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'workshop', 'user', 'status',)
    list_filter = ('status', 'workshop',)
    form = make_ajax_form(WorkshopConnection, {
        'user': 'moodleuser_lookup'
    })

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


@admin.register(ContestConnection)
class ContestConnectionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'contest', 'user',)
    form = make_ajax_form(ContestConnection, {
        'user': 'moodleuser_lookup'
    })


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
    list_display = ('__str__', 'status', 'visibility',)
    inlines = (ContestAdminInline,
               MonitorAdminInline)

    def is_new_object_in_form_creating(self, form):
        data = form.cleaned_data
        return data and not data.get('id') and not data.get('DELETE')

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
admin.site.register(Statement)
