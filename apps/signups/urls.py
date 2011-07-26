from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('signups.views',
  url(r'^$', 'sign_up', name='sign_up'),
  url(r'^(?P<pagination_page>\d+)/$', 'sign_up', name='sign_up'),
  url(r'^comment/$', 'comment_sign_up', name='sign_up_comment'),
  url(r'^comment/(?P<comment_id>\d+)/edit/$',
      'edit_comment_sign_up', name='sign_up_edit_comment'),
  url(r'^comment/(?P<comment_id>\d+)/reply/$',
      'comment_sign_up', name='sign_up_reply'),
  url(r'^comment/(?P<comment_id>\d+)/add_participant/$',
      'accept_sign_up', name='sign_up_add_participant'),
  (r'^comment/(?P<comment_id>\d+)/add_organizer/$',
      'accept_sign_up', {'as_organizer': True}, 'sign_up_add_organizer'),
)
