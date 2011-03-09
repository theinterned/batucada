from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('course_tasks.views',
  url(r'^(?P<task_id>\d+)/$', 'show',
      name='task_show'),
  url(r'^create/$', 'create',
      name='create_task'),
  url(r'^create/project/(?P<project_id>\d+)/$',
      'create_project_task',
      name='create_project_task'),
)
