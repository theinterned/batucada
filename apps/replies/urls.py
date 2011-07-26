from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('replies.views',
  url(r'^$', 'comment_page', name='page_comment'),
  url(r'^(?P<comment_id>\d+)/$', 'show_comment',
      name='comment_show'),
  url(r'^(?P<comment_id>\d+)/edit/$', 'edit_comment',
      name='comment_edit'),
  url(r'^(?P<comment_id>\d+)/delete/$', 'delete_restore_comment',
      name='comment_delete'),
  url(r'^(?P<comment_id>\d+)/restore/$', 'delete_restore_comment',
      name='comment_restore'),
  url(r'^(?P<comment_id>\d+)/reply/$', 'comment_page',
      name='comment_reply'),
)
