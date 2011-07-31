from django.conf.urls.defaults import patterns, url

from activity import feeds


urlpatterns = patterns('',
    url(r'^activity/(?P<activity_id>[\d]+)/$', 'activity.views.index',
        name='activity_index'),
    url(r'^activity/(?P<activity_id>[\d]+)/delete/$',
      'activity.views.delete_restore', name='activity_delete'),
    url(r'^activity/(?P<activity_id>[\d]+)/restore/$',
      'activity.views.delete_restore', name='activity_restore'),
    url(r'^(?P<username>[\w\-\. ]+)/feed/$', feeds.ProfileActivityFeed(),
        name='activity_profile_feed'),
    url(r'^(?P<username>[\w\-\. ]+)/dashboard/feed/$',
        feeds.DashboardActivityFeed(), name='activity_dashboard_feed'),
    url(r'^groups/(?P<slug>[\w\- ]+)/feed/$', feeds.ProjectActivityFeed(),
        name='activity_project_feed'),
    url(r'^feed/$', feeds.PublicActivityFeed(),
        name='activity_public_feed'),
)
