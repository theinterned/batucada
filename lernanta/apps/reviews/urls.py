from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
  url(r'^pending/$', 'reviews.views.pending',
      name='projects_pending_review'),
  url(r'^under_review/$', 'reviews.views.under_review',
      name='projects_under_review'),
  url(r'^accepted/$', 'reviews.views.accepted',
      name='accepted_projects'),
  url(r'^projects/(?P<slug>[\w-]+)/$', 'reviews.views.show_project_reviews',
      name='show_project_reviews'),
    url(r'^projects/(?P<slug>[\w-]+)/review/$', 'reviews.views.review_project',
      name='review_project'),
)
