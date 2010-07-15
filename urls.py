from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'',         include('dashboard.urls')),
    (r'^openid/', include('django_openid_auth.urls')),
    (r'^admin/',  include(admin.site.urls)),
)
