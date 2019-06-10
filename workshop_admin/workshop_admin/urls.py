from ajax_select import urls as ajax_select_urls
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from tz_detect import urls as tz_detect_urls

urlpatterns = [
    url(r'^tz_detect/', include(tz_detect_urls)),
    url(r'^ajax_select/', include(ajax_select_urls)),
    path('grappelli/', include('grappelli.urls')),
    url(r'^admin/', admin.site.urls),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
