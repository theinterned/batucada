from django.conf.urls.defaults import *

from activity.feeds import UserActivityAtomFeed, UserNewsActivityAtomFeed, ObjectActivityAtomFeed

urlpatterns = patterns('',
    url(r'^(?P<activity_id>\d+)/$', 'activity.views.index',
        name='activity_index'),
    url(r'^(?P<username>[\w ]+)/stream/$', UserActivityAtomFeed(),
        name='activity_feed_user'),
    url(r'^(?P<object_id>\d+)/stream/$', ObjectActivityAtomFeed(),
        name='activity_feed_object'),
    url(r'^(?P<username>[\w ]+)/events/stream/$', UserNewsActivityAtomFeed(),
        name='activity_feed_user_news'),
)
