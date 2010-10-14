from django.conf.urls.defaults import *

urlpatterns = patterns('',
  (r'^gallery/$',          'projects.views.gallery'),
  (r'^create/$',           'projects.views.create'),
  (r'^(?P<slug>[\w-]+)/$', 'projects.views.show', {}, 'projects_show'),
)
