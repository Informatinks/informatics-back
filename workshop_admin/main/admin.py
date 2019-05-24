import datetime

from ajax_select import make_ajax_form
from ajax_select.admin import AjaxSelectAdminTabularInline, AjaxSelectAdmin
from django.contrib import admin
from moodle.models import Statement

from .models import WorkshopConnection, Workshop, ContestConnection, Contest, WorkshopMonitor


@admin.register(WorkshopConnection)
class WorkshopConnectionAdmin(admin.ModelAdmin):
    form = make_ajax_form(WorkshopConnection, {
        'user': 'moodleuser_lookup'
    })


@admin.register(ContestConnection)
class ContestConnectionAdmin(admin.ModelAdmin):
    form = make_ajax_form(ContestConnection, {
        'user': 'moodleuser_lookup'
    })


class ContestAdmin(AjaxSelectAdmin):
    readonly_fields = ('author', 'created_at',)

    form = make_ajax_form(Contest, {
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


class ContestAdminInline(AjaxSelectAdminTabularInline):
    model = Contest
    ordering = ('position',)
    exclude = ('author', 'created_at',)
    form = make_ajax_form(Contest, {
        'statement': 'statement_lookup'
    })


class MonitorAdminInline(admin.TabularInline):
    model = WorkshopMonitor


class WorkshopAdmin(admin.ModelAdmin):
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
    pass


admin.site.register(Contest, ContestAdmin)
admin.site.register(Workshop, WorkshopAdmin)
admin.site.register(WorkshopMonitor, WorkshopMonitorAdmin)
admin.site.register(Statement)
