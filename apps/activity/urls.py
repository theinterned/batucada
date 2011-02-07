from django.conf.urls.defaults import patterns, url

from activity import feeds


urlpatterns = patterns('',
    url(r'^activity/(?P<activity_id>[\d]+)/$', 'activity.views.index',
        name='activity_index'),
    url(r'^(?P<username>[\w\- ]+)/feed$', feeds.UserActivityFeed(),
        name='activity_user_feed'),
    url(r'^projects/(?P<project>[\w\- ]+)/feed$', feeds.ProjectActivityFeed(),
        name='activity_project_feed'),
    url(r'^feed$', feeds.DashboardFeed(),
        name='activity_dashboard_feed'),
)
