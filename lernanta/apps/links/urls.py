from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('links.views',
  url(r'^index/link/(?P<counter>\d+)/up/$', 'link_index_up',
      name='link_index_up'),
  url(r'^index/link/(?P<counter>\d+)/down/$', 'link_index_down',
      name='link_index_down'),
)
