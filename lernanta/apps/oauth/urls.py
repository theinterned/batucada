from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('',
    url(r'^missing_redirect_uri/?$', 'oauth.views.missing_redirect_uri',
        name='oauth_missing_redirect_uri'),

    url(r'^authorize/?$', 'oauth.views.authorize',
        name='oauth_authorize'),

    url(r'^token/?$', 'oauth2app.token.handler',
        name='oauth_token_handler'),

    url(r'^test/$', 'oauth.views.test',
        name='oauth_test'),
)
