from django.conf.urls.defaults import *

urlpatterns = patterns('',
  (r'^edit/$',             'profiles.views.edit'),
  (r'^upload-image/$',     'profiles.views.upload_image'),
  (r'^skills/$',           'profiles.views.skills'),
  (r'^skills/delete/$',    'profiles.views.delete_skill'),
  (r'^interests/$',        'profiles.views.interests'),
  (r'^interests/delete/$', 'profiles.views.delete_interest'),

  (r'^(?P<username>[\w ]+)/$', 'profiles.views.show'),
)
