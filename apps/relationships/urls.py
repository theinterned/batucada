from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
    url(r'^following/', 'relationships.views.following',
        name='relationships_following'),
    url(r'^followers/', 'relationships.views.followers',
        name='relationships_followers'),
    url(r'^follow/', 'relationships.views.follow',
        name='relationships_follow'),
    url(r'^unfollow/', 'relationships.views.unfollow',
        name='relationships_unfollow'),
)
