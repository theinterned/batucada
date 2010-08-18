from django.conf import settings
from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

from accountmanager.views import handle as accountmanager_handle

urlpatterns = patterns('',
    (r'',                include('dashboard.urls')),
    (r'',                include('users.urls')),
    (r'',                include('wellknown.urls')),
    (r'^profile/',       include('profiles.urls')),
    (r'^relationships/', include('relationships.urls')),
    (r'^admin/',         include(admin.site.urls)),

    (r'^meta/amcd.json$',accountmanager_handle),
)

if settings.DEBUG:
    media_url = settings.MEDIA_URL.lstrip('/').rstrip('/')
    urlpatterns += patterns('',
        (r'^%s/(?P<path>.*)$' % media_url, 'django.views.static.serve',
         { 'document_root': settings.MEDIA_ROOT }
        ),
    )

