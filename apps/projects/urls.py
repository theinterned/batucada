from django.conf.urls.defaults import *

urlpatterns = patterns('',
  (r'^(?P<project>\w+)/$', 'projects.views.show'),
)
