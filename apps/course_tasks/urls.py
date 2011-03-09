from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('course_tasks.views',
  url(r'^(?P<todo_id>\d+)/$', 'show',
      name='todos_show'),
  url(r'^create/$', 'create',
      name='todos_create'),
  url(r'^create/project/(?P<project_id>\d+)/$',
      'create_project_todo',
      name='todos_create_project'),
)
