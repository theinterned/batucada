from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('',
  url(r'^settings/', 'preferences.views.settings',
      name='preferences_settings'),
  url(r'^delete/', 'preferences.views.delete',
      name='preferences_delete'),
)
