from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
  url(r'^scoreboard/$', 'tracker.views.scoreboard',
      name='metrics_scoreboard'),
)
