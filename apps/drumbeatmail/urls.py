from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import redirect_to


urlpatterns = patterns('',
    url(r'^$', redirect_to, {'url': 'inbox/'}),
    url(r'^inbox/$', 'drumbeatmail.views.inbox',
        name='drumbeatmail_inbox'),
    url(r'^compose/$', 'drumbeatmail.views.compose',
        name='drumbeatmail_compose'),
)
