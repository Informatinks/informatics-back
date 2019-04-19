from django.contrib import admin

# Register your models here.
from .models import WorkshopConnection, Workshop, ContestConnection, Contest


admin.site.register(Contest)
admin.site.register(ContestConnection)
admin.site.register(Workshop)
admin.site.register(WorkshopConnection)
