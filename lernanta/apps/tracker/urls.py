from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
  url(r'^scoreboard/$', 'tracker.views.scoreboard',
      name='metrics_scoreboard'),
  url(r'^scoreboard/users/$', 'tracker.views.scoreboard_users',
      name='metrics_scoreboard_users'),
  url(r'^scoreboard/top-groups-comments/$', 'tracker.views.scoreboard_top_groups_by_comments',
      name='metrics_scoreboard_top_groups_comments'),
  url(r'^scoreboard/top-groups-joins/$', 'tracker.views.scoreboard_top_groups_by_joins',
      name='metrics_scoreboard_top_groups_joins'),
  url(r'^scoreboard/groups/$', 'tracker.views.scoreboard_groups',
      name='metrics_scoreboard_groups'),
)
