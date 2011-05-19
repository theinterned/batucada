from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
  url(r'^(?P<slug>[\w\-\. ]+)/$', 'pages.views.show_page',
      name='page_show'),

)
