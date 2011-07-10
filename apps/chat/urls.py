from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('',
  url(r'^$', 'chat.views.chat',
      name='chat'),
)
