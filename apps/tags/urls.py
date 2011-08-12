from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
  url(r'^(?P<tag_slug>[\w\-\. ]+)/$', 'tags.views.list_tagged_all',
      name='tags_tagged_list'),

)
