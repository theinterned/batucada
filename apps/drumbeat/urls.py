from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('django.views.generic.simple',
   url(r'^terms-of-service/$', 'direct_to_template', {
       'template': 'drumbeat/terms-of-service.html',
   }, name='drumbeat_tos'),
   url(r'^about/$', 'direct_to_template', {
       'template': 'drumbeat/about.html',
   }, name='drumbeat_about'),
)

urlpatterns += patterns('',
   url(r'^abuse/(?P<content_type>[\w ]+)/(?P<pk>\w+)/$',
       'drumbeat.views.report_abuse',
       name='drumbeat_abuse'),
)
