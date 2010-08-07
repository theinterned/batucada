from django.conf.urls.defaults import *

urlpatterns = patterns('',
  (r'^login/',         'users.views.login'),
  (r'^logout/',        'users.views.logout'),
  (r'^register/',      'users.views.register'),
  (r'^forgot/',        'users.views.forgot_password'),

  (r'^profile/edit/',   'users.views.profile'),
  (r'^profile/create/', 'users.views.profile_create'),
  (r'^profile/(?P<username>[\w ]+)$', 'users.views.profile_detail'),

  (r'^users/list/', 'users.views.user_list'),
  
  (r'^openid/login/',          'users.views.login_openid'),
  (r'^openid/login_complete/', 'users.views.login_complete'),
  (r'^openid/register/',       'users.views.register_openid'),

  (r'^reset/(?P<token>\w+)/(?P<username>[\w ]+)/$',
   'users.views.reset_password_form'),
  (r'^confirm/(?P<token>\w+)/(?P<username>[\w ]+)/$',
   'users.views.confirm_registration'),
)
