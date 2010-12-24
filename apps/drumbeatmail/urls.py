from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import redirect_to


urlpatterns = patterns('',
    url(r'^$', redirect_to, {'url': 'inbox/'}),
    url(r'^inbox/$', 'drumbeatmail.views.inbox',
        name='drumbeatmail_inbox'),
    url(r'^inbox/(?P<filter>[\w-]+)/$', 'drumbeatmail.views.inbox_filtered',
        name='drumbeatmail_inbox_filtered'),
    url(r'^outbox/$', 'drumbeatmail.views.outbox',
        name='drumbeatmail_outbox'),
    url(r'^compose/$', 'drumbeatmail.views.compose',
        name='drumbeatmail_compose'),
    url(r'^reply/(?P<message>[\d])/$', 'drumbeatmail.views.reply',
        name='drumbeatmail_reply'),
)
