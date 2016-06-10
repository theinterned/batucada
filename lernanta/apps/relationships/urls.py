from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
    url(r'^follow/(?P<object_type>[\w-]+)/(?P<slug>[\w\-\. ]+)/$',
        'relationships.views.follow',
        name='relationships_follow'),
    url(r'^unfollow/(?P<object_type>[\w-]+)/(?P<slug>[\w\-\. ]+)/$',
        'relationships.views.unfollow',
        name='relationships_unfollow'),
)
