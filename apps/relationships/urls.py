from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^following/', 'relationships.views.following'),
    (r'^followers/', 'relationships.views.followers'),
    (r'^follow/',    'relationships.views.follow'),
    (r'^unfollow/',  'relationships.views.unfollow'),
)
