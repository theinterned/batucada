from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
  url(r'^create/$', 'content.views.create_page',
      name='page_create'),
  url(r'^(?P<page_slug>[\w-]+)/$', 'content.views.show_page',
      name='page_show'),
  url(r'^(?P<page_slug>[\w-]+)/edit/$', 'content.views.edit_page',
      name='page_edit'),
  url(r'^(?P<page_slug>[\w-]+)/comment/$', 'content.views.comment_page',
      name='page_comment'),
  url(r'^(?P<page_slug>[\w-]+)/history/$', 'content.views.history_page',
      name='page_history'),
  url(r'^(?P<page_slug>[\w-]+)/history/(?P<version_id>\d+)/$', 'content.views.version_page',
      name='page_version'),
  url(r'^(?P<page_slug>[\w-]+)/history/(?P<version_id>\d+)/restore/$', 'content.views.restore_version',
      name='version_restore'),
)
