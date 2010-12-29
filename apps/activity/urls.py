from django.conf.urls.defaults import patterns, url

from activity.feeds import UserActivityFeed


urlpatterns = patterns('',
    url(r'^activity/(?P<activity_id>[\d]+)/', 'activity.views.index',
        name='activity_index'),
    url(r'^activity/delete/$', 'activity.views.delete',
        name='activity_delete'),
    url(r'^(?P<username>[\w-]+)/feed', UserActivityFeed(),
        name='activity_user_feed'),
)
