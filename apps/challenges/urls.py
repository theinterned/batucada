from django.conf.urls.defaults import patterns, url, include
from models import Submission
from challenges.feeds import (ChallengesFeed, ProjectChallengesFeed,
                              SubmissionsFeed)
from voting.views import vote_on_object

vote_dict = {
  'model': Submission,
  'template_object_name': 'submission',
  'allow_xmlhttprequest': True,
}

urlpatterns = patterns('',
  # Challenges
  url(r'^create/project/(?P<project_id>\d+)/$',
      'challenges.views.create_challenge',
      name='challenges_create'),
  url(r'^(?P<slug>[\w-]+)/edit/$', 'challenges.views.edit_challenge',
      name='challenges_edit'),
  url(r'^(?P<slug>[\w-]+)/edit/image/$',
      'challenges.views.edit_challenge_image',
      name='challenges_edit_image'),
  url(r'^(?P<slug>[\w-]+)/edit/image/async$',
      'challenges.views.edit_challenge_image_async',
      name='challenges_edit_image_async'),

  url(r'^(?P<challenge>[\w-]+)/submissions/feed/$', SubmissionsFeed(),
      name='challenges_submissions_feed'),
  url(r'^(?P<project>[\w-]+)/feed/$', ProjectChallengesFeed(),
      name='challenges_project_feed'),
  url(r'^feed/$', ChallengesFeed(), name='challenges_feed'),

  url(r'^(?P<slug>[\w-]+)/$', 'challenges.views.show_challenge',
      name='challenges_show'),
  url(r'^(?P<slug>[\w-]+)/full$', 'challenges.views.show_challenge_full',
      name='challenges_show_full'),
  url(r'^(?P<slug>[\w-]+)/contact$', 'challenges.views.contact_entrants',
      name='challenges_contact_entrants'),

  # Submissions
  url(r'^(?P<slug>[\w-]+)/submission/create/$',
      'challenges.views.create_submission',
      name='submissions_create'),
  url(r'^(?P<slug>[\w-]+)/submission/(?P<submission_id>\d+)/$',
      'challenges.views.show_submission',
      name='submission_show'),
  url(r'^(?P<slug>[\w-]+)/submission/(?P<submission_id>\d+)/edit/$',
      'challenges.views.edit_submission',
      name='submission_edit'),
  url(r'^(?P<slug>[\w-]+)/submission/(?P<submission_id>\d+)/edit/desc/$',
      'challenges.views.edit_submission_description',
      name='submission_edit_description'),
  url(r'^(?P<slug>[\w-]+)/submission/(?P<submission_id>\d+)/edit/share/$',
      'challenges.views.edit_submission_share',
      name='submission_edit_share'),


  # Voting
  url(r'^submission/(?P<object_id>\d+)/(?P<direction>up|clear)vote/?$',
      vote_on_object, vote_dict, name='submission_vote'),
  url(r'^submission/(?P<submission_id>\d+)/voter_details/',
      'challenges.views.submissions_voter_details',
      name='submissions_voter_details'),

  # Judges
  url(r'^(?P<slug>[\w-]+)/judges/$', 'challenges.views.challenge_judges',
      name='challenges_judges'),
  url(r'^(?P<slug>[\w-]+)/judges/delete/(?P<judge>[\d]+)/$',
      'challenges.views.challenge_judges_delete',
      name='challenges_judge_delete'),

  (r'^comments/', include('django.contrib.comments.urls')),
)
