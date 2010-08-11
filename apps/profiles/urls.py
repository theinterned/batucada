from django.conf.urls.defaults import *

urlpatterns = patterns('',
  (r'^edit/$',             'profiles.views.edit'),
  (r'^upload-image/$',     'profiles.views.upload_image'),
  (r'^numbers/$',          'profiles.views.contact_numbers'),
  (r'^numbers/delete/$',   'profiles.views.delete_number'),
  (r'^links/$',            'profiles.views.links'),
  (r'^links/delete/$',     'profiles.views.delete_link'),
  (r'^skills/$',           'profiles.views.skills'),
  (r'^skills/delete/$',    'profiles.views.delete_skill'),
  (r'^interests/$',        'profiles.views.interests'),
  (r'^interests/delete/$', 'profiles.views.delete_interest'),

  (r'^(?P<username>[\w ]+)/$', 'profiles.views.show'),
)
