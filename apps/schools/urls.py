from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
    url(r'^(?P<slug>[\w-]+)/$', 'schools.views.home', name='school_home'),
)
