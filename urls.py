from django.conf import settings
from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'',                include('dashboard.urls')),
    (r'',                include('users.urls')),
    (r'',                include('wellknown.urls')),
    (r'^profile/',       include('profiles.urls')),
    (r'^relationships/', include('relationships.urls')),
    (r'^accountmanager/',include('accountmanager.urls')),
    (r'^activity/',      include('activity.urls')),
    (r'^admin/',         include(admin.site.urls)),
)

if settings.DEBUG:
    media_url = settings.MEDIA_URL.lstrip('/').rstrip('/')
    urlpatterns += patterns('',
        (r'^%s/(?P<path>.*)$' % media_url, 'django.views.static.serve',
         { 'document_root': settings.MEDIA_ROOT }
        ),
    )

