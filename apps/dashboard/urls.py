from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
    url(r'^$', 'dashboard.views.splash', name='splash'),
    url(r'^dashboard/$', 'dashboard.views.dashboard', name='dashboard'),
    url(r'^broadcasts/hide_welcome/$', 'dashboard.views.hide_welcome',
        name='dashboard_hide_welcome'),
)
