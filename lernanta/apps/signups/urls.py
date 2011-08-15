from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('signups.views',
  url(r'^$', 'show_signup', name='sign_up'),
  url(r'^edit/$', 'edit_signup', name='edit_signup'),
  url(r'^answer/$', 'answer_sign_up', name='sign_up_answer'),
  url(r'^answer/(?P<answer_id>\d+)/$',
      'show_signup_answer', name='show_signup_answer'),
  url(r'^answer/(?P<answer_id>\d+)/edit/$',
      'edit_answer_sign_up', name='sign_up_edit_answer'),
  url(r'^answer/(?P<answer_id>\d+)/delete/$',
      'delete_restore_signup_answer', name='delete_signup_answer'),
  url(r'^answer/(?P<answer_id>\d+)/restore/$',
      'delete_restore_signup_answer', name='restore_signup_answer'),
  url(r'^answer/(?P<answer_id>\d+)/accept_participant/$',
      'accept_sign_up', name='sign_up_accept_participant'),
  (r'^answer/(?P<answer_id>\d+)/accept_organizer/$',
      'accept_sign_up', {'as_organizer': True}, 'sign_up_accept_organizer'),
)
