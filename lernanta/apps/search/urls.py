from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('',
  url(r'^$', 'search.views.search',
      name='search'),
)
