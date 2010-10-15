from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'dashboard.views.index', name='dashboard_index'),
)
