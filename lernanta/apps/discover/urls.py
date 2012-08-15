from django.conf.urls.defaults import patterns, url, include

urlpatterns = patterns('',
    url(r'^$', 'discover.views.learn',
        name='discover_learn'),

    url(r'^schools/(?P<school_slug>[\w-]+)/', 'discover.views.schools',
        name='discover_schools'),

    url(r'^featured/(?P<feature>[\w-]+)/', 'discover.views.featured',
        name='discover_featured'),

    url(r'^find/$', 'discover.views.find',
        name='discover_find'),

    url(r'^tags/$', 'discover.views.learn_tags',
        name='discover_learn_tags'),
)
