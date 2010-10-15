from django.conf.urls.defaults import *

urlpatterns = patterns('',
  url(r'^(?P<status_id>\d+)/$', 'statuses.views.show',
      name='statuses_show'),
  url(r'^create/$', 'statuses.views.create',
      name='statuses_create'),
)
