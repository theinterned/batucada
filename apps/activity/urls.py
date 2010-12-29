from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('',
    url(r'^(?P<activity_id>[\d]+)/', 'activity.views.index',
        name='activity_index'),
    url(r'^delete/$', 'activity.views.delete',
        name='activity_delete'),
)
