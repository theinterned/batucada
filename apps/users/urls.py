from django.conf.urls.defaults import patterns, url

from users import forms

urlpatterns = patterns('',

  # Login / auth urls
  url(r'^login/', 'users.views.login',
      name='users_login'),
  url(r'^logout/', 'users.views.logout',
      name='users_logout'),

  # Reset password urls
  url(r'^forgot/$',
      'django.contrib.auth.views.password_reset',
      {'template_name': 'users/forgot_password.html',
       'email_template_name': 'users/emails/forgot_password.txt'},
      name='users_forgot_password'),

  url(r'^forgot/sent/$',
      'django.contrib.auth.views.password_reset_done',
      {'template_name': 'users/forgot_password_done.html'},
      name='users_forgot_password_done'),

  url(r'^forgot/(?P<uidb36>[-\w]+)/(?P<token>[-\w]+)$',
      'django.contrib.auth.views.password_reset_confirm',
      {'template_name': 'users/forgot_password_confirm.html',
       'set_password_form': forms.SetPasswordForm},
      name='users_forgot_password_confirm'),

  url(r'^forgot/complete/$',
      'django.contrib.auth.views.password_reset_complete',
      {'template_name': 'users/forgot_password_complete.html'},
      name='users_forgot_password_complete'),


  # Public pages
  url(r'^users/list/', 'users.views.user_list',
      name='users_user_list'),

  # Registration urls
  url(r'^register/', 'users.views.register',
      name='users_register'),
  url(r'^confirm/resend/(?P<username>[\w ]+)/$',
      'users.views.confirm_resend',
      name='users_confirm_resend'),
  url(r'^confirm/(?P<token>\w+)/(?P<username>[\w ]+)/$',
      'users.views.confirm_registration',
      name='users_confirm_registration'),

  # Profile urls
  url('^(?P<username>[\w ]+)/$', 'users.views.profile_view',
      name='users_profile_view'),
  url('^profile/edit/$', 'users.views.profile_edit',
      name='users_profile_edit'),
)
