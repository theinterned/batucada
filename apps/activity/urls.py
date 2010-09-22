from django.conf.urls.defaults import *

from activity.feeds import UserActivityAtomFeed, ObjectActivityAtomFeed

urlpatterns = patterns('',
    (r'activity/(?P<activity_id>\d+)/$', 'activity.views.index'),
    (r'(?P<username>[\w ]+)/stream/$', UserActivityAtomFeed()),
    (r'(?P<object_id>\d+)/stream/$', ObjectActivityAtomFeed()),
)
