from django.conf.urls.defaults import *

urlpatterns = patterns('',
  url(r'^gallery/$', 'projects.views.gallery',
      name='projects_gallery'),
  url(r'^create/$', 'projects.views.create',
      name='projects_create'),
  url(r'^(?P<slug>[\w-]+)/edit/$', 'projects.views.edit',
      name='projects_edit'),
  url(r'^(?P<slug>[\w-]+)/$', 'projects.views.show',
      name='projects_show'),
  url(r'^(?P<slug>[\w-]+)/contactfollowers/$', 'projects.views.contact_followers',
      name='projects_contact_followers'),
)
