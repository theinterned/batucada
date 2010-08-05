from django.conf.urls.defaults import *

urlpatterns = patterns('',
  (r'^forgot/', 'forgetful.views.forgot'),
  (r'^reset/(?P<token>\w+)/(?P<username>[\w ]+)/$', 'forgetful.views.reset'),
)
