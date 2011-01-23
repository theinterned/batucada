from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
  url(r'^(?P<todo>\d+)/$', 'todos.views.show',
      name='todos_show'),
  url(r'^create/$', 'todos.views.create',
      name='todos_create'),
  url(r'^create/project/(?P<project_id>\d+)/$',
      'todos.views.create_project_todo',
      name='todos_create_project'),
)
