from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('django.views.generic.simple',
   url(r'^terms-of-service/$', 'direct_to_template', {
       'template': 'drumbeat/terms-of-service.html',
   }, name='drumbeat_tos'),
   url(r'^about/$', 'direct_to_template', {
       'template': 'drumbeat/about.html',
   }, name='drumbeat_about'),
   url(r'^editing-help/$', 'direct_to_template', {
        'template': 'drumbeat/editing.html',
   }, name='drumbeat_editing'),
)

urlpatterns += patterns('',
   url(r'^abuse/(?P<model>[\w ]+)/(?P<app_label>[\w ]+)/(?P<pk>\w+)/$',
       'drumbeat.views.report_abuse',
       name='drumbeat_abuse'),
)
