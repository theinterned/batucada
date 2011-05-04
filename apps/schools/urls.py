from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
    url(r'^(?P<slug>[\w-]+)/$', 'schools.views.home', name='school_home'),
    url(r'^(?P<slug>[\w-]+)/edit/$', 'schools.views.edit', name='schools_edit'),
    url(r'^(?P<slug>[\w-]+)/edit/featured/$',
      'schools.views.edit_featured',
      name='schools_edit_featured'),
    url(r'^(?P<slug>[\w-]+)/edit/featured/(?P<project_slug>[\w-]+)/delete/$',
      'schools.views.edit_featured_delete',
      name='schools_edit_featured_delete'),
    url(r'^(?P<slug>[\w-]+)/edit/featured/matching_non_featured/$',
      'schools.views.matching_non_featured',
      name='matching_non_featured'),
)
