from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
    url(r'^follow/', 'relationships.views.follow',
        name='relationships_follow'),
    url(r'^unfollow/', 'relationships.views.unfollow',
        name='relationships_unfollow'),
)
