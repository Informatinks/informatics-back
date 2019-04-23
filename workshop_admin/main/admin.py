import datetime

from django.contrib import admin

from .models import WorkshopConnection, Workshop, ContestConnection, Contest


admin.site.register(ContestConnection)
admin.site.register(WorkshopConnection)


class ContestAdmin(admin.ModelAdmin):

    readonly_fields = ('author', 'created_at', )

    @classmethod
    def add_default_fields(cls, request, obj: Contest):
        obj.author_id = request.user.pk
        obj.created_at = datetime.datetime.utcnow()

    def save_model(self, request, obj: Contest, form, change):
        self.add_default_fields(request, obj)
        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        return ['author', 'created_at']


class ContestAdminInline(admin.TabularInline):
    model = Contest
    ordering = ('position', )
    readonly_fields = ('author', 'created_at',)


class WorkshopAdmin(admin.ModelAdmin):
    inlines = (ContestAdminInline, )

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


admin.site.register(Contest, ContestAdmin)
admin.site.register(Workshop, WorkshopAdmin)
