from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('pages.views',
  url(r'^get-involved/$', direct_to_template,
    {'template': 'pages/get_involved_page.html'},
    name='static_get_involved_page'),
  url(r'^jobs/$', 'jobs_page', name='static_jobs_page'),
  url(r'^(?P<slug>[\w\-\. ]+)/$', 'show_page', name='static_page_show'),
)
