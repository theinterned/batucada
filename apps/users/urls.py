from django.conf.urls.defaults import *

urlpatterns = patterns('',
  (r'^login/',    'users.views.login'),
  (r'^logout/',   'users.views.logout'),
  (r'^register/', 'users.views.register'),
  (r'^forgot/',   'users.views.forgot'),

  (r'^openid/login/',   'users.views.login_openid'),
  (r'^login_complete/', 'users.views.login_complete'),
)
