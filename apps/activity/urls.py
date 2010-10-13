from django.conf.urls.defaults import *

from activity.feeds import UserActivityAtomFeed, ObjectActivityAtomFeed

urlpatterns = patterns('',
    (r'activity/(?P<activity_id>\d+)/$', 'activity.views.index'),
                       
    url(r'(?P<username>[\w ]+)/stream/$', UserActivityAtomFeed(),
        name='activity_feed_user'),
    url(r'(?P<object_id>\d+)/stream/$', ObjectActivityAtomFeed(),
        name='activity_feed_object'),
)
