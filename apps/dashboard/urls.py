from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
    url(r'^$', 'dashboard.views.index', name='dashboard_index'),
    url(r'^broadcasts/hide_welcome/$', 'dashboard.views.hide_welcome',
        name='dashboard_hide_welcome'),
)
