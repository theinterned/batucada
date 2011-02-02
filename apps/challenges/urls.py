from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
  # Challenges
  url(r'^create/project/(?P<project_id>\d+)/$',
      'challenges.views.create_challenge',
      name='challenges_create'),

  url(r'^(?P<slug>[\w-]+)/$', 'challenges.views.show_challenge',
      name='challenges_show'),

  # Submissions
  url(r'^(?P<slug>[\w-]+)/submission/create', 
      'challenges.views.create_submission',
      name='submission_create')
)
