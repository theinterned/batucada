from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
  url(r'^create/$', 'content.views.create_page',
      name='page_create'),
  url(r'^(?P<page_slug>[\w-]+)/$', 'content.views.show_page',
      name='page_show'),
  url(r'^(?P<page_slug>[\w-]+)/edit/$', 'content.views.edit_page',
      name='page_edit'),
  url(r'^(?P<page_slug>[\w-]+)/comment/$', 'content.views.comment_page',
      name='page_comment')
)
