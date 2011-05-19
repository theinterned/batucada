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
   url(r'^journalism/participate/$', 'direct_to_template', {
        'template': 'drumbeat/journalism/participate.html',
   }, name='drumbeat_journalism_participate'),
   url(r'^journalism/process/$', 'direct_to_template', {
        'template': 'drumbeat/journalism/process.html',
   }, name='drumbeat_journalism_process'),
   url(r'^journalism/about/$', 'direct_to_template', {
        'template': 'drumbeat/journalism/about.html',
   }, name='drumbeat_journalism_about'),
)

urlpatterns += patterns('',
   url(r'^abuse/(?P<type>[\w ]+)/(?P<obj>\w+)/$',
       'drumbeat.views.report_abuse',
       name='drumbeat_abuse'),
   url(r'^journalism/$',
       'drumbeat.views.journalism',
       name='drumbeat_journalism'),
)
