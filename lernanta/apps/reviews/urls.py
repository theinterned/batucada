from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
  url(r'^$', 'reviews.views.show_new',
      name='reviews_show_new'),
  url(r'^reviewed/$', 'reviews.views.show_reviewed',
      name='reviews_show_reviewed'),
  url(r'^groups/(?P<slug>[\w-]+)/$', 'reviews.views.show_project_reviews',
      name='show_project_reviews'),
    url(r'^groups/(?P<slug>[\w-]+)/review/$', 'reviews.views.review_project',
      name='review_project'),
)
