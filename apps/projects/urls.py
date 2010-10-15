from django.conf.urls.defaults import *

urlpatterns = patterns('',
  url(r'^gallery/$', 'projects.views.gallery',
      name='projects_gallery'),
  url(r'^create/$', 'projects.views.create',
      name='projects_create'),
  url(r'^(?P<slug>[\w-]+)/$', 'projects.views.show',
      name='projects_show'),
)
