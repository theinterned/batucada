from django.conf.urls.defaults import *

urlpatterns = patterns('',
  (r'^edit/$',          'profiles.views.edit'),
  (r'^upload-image/$',  'profiles.views.upload_image'),
  (r'^numbers/$',       'profiles.views.contact_numbers'),
  (r'^numbers/delete/$','profiles.views.delete_number'),
  (r'^links/$',         'profiles.views.profile_links'),
  (r'^skills/$',        'profiles.views.skills'),
  (r'^interests/$',     'profiles.views.interests'),

  (r'^(?P<username>[\w ]+)/$', 'profiles.views.show'),
)
