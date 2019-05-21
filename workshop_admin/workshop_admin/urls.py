from django.conf.urls import url
from django.contrib import admin
from django.urls import include, path
from ajax_select import urls as ajax_select_urls
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    url(r'^ajax_select/', include(ajax_select_urls)),
    path('grappelli/', include('grappelli.urls')),
    url(r'^admin/', admin.site.urls),
]  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
