from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
  url(r'^edit/$', 'profiles.views.edit',
      name='profiles_edit'),                 
  url(r'^upload-image/$', 'profiles.views.upload_image',
      name='profiles_upload_image'),
  url(r'^skills/$', 'profiles.views.skills',
      name='profiles_skills'),
  url(r'^skills/delete/$', 'profiles.views.delete_skill',
      name='profiles_delete_skill'),
  url(r'^interests/$', 'profiles.views.interests',
      name='profiles_interests'),
  url(r'^interests/delete/$', 'profiles.views.delete_interest',
      name='profiles_delete_interest'),                       
  url(r'^(?P<username>[\w ]+)/$', 'profiles.views.show',
      name='profiles_show'),
)
