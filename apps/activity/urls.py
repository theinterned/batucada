from django.conf.urls.defaults import *

from activity.feeds import UserActivityFeed, ObjectActivityFeed

urlpatterns = patterns('',
    (r'^people/(?P<actor>[\w ]+)/feed/$', UserActivityFeed()),
    (r'^objects/(?P<object_id>)/feed/$', ObjectActivityFeed()),
)
