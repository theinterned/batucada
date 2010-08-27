from django.conf.urls.defaults import *

from activity.feeds import UserActivityFeed, ObjectActivityFeed

urlpatterns = patterns('',
    (r'activity/(?P<activity_id>\d+)/$', 'activity.views.index'),
    (r'(?P<username>[\w ]+)/stream/$', UserActivityFeed()),
    (r'(?P<object_id>\d+)/stream/$', ObjectActivityFeed()),
)
