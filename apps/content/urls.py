from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
  url(r'^(?P<slug>[\w-]+)/$', 'content.views.show_page',
      name='page_show'),
  url(r'^(?P<slug>[\w-]+)/edit/$', 'content.views.edit_page',
      name='page_edit'),
)
