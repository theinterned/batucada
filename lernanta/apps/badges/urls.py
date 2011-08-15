from django.conf.urls.defaults import patterns, url, include


urlpatterns = patterns('',
  (r'^obi/', include('django_obi.urls')),
  url(r'^(?P<slug>[\w-]+)/$', 'badges.views.badge_description',
      name='badge_description'),
)
