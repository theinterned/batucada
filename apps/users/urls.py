from django.conf.urls.defaults import *

urlpatterns = patterns('',
  url(r'^login/', 'users.views.login',
      name='users_login'),
  url(r'^logout/', 'users.views.logout',
      name='users_logout'),
  url(r'^register/', 'users.views.register',
      name='users_register'),
  url(r'^forgot/', 'users.views.forgot_password',
      name='users_forgot_password'),

  url(r'^users/list/', 'users.views.user_list',
      name='users_user_list'),
  
  url(r'^openid/login/', 'users.views.login_openid',
      name='users_login_openid'),
  url(r'^openid/login_complete/', 'users.views.login_complete',
      name='users_login_complete'),
  url(r'^openid/register/', 'users.views.register_openid',
      name='users_register_openid'),

  url(r'^reset/(?P<token>\w+)/(?P<username>[\w ]+)/$',
      'users.views.reset_password_form',
      name='users_reset_password_form'),
                       
  url(r'^confirm/(?P<token>\w+)/(?P<username>[\w ]+)/$',
      'users.views.confirm_registration',
      name='users_confirm_registration'),
)
