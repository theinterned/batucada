from django.conf.urls.defaults import *

urlpatterns = patterns('',
  (r'^(?P<status_id>\d+)/$', 'statuses.views.show'),
  (r'^create/$', 'statuses.views.create'),
)
