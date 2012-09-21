from django.conf.urls.defaults import patterns, url, include

urlpatterns = patterns('',
    url(r'^create/$', 'courses.views.create_course',
        name='courses_create'),

    url(r'^(?P<course_id>[\d]+)/$', 
        'courses.views.course_slug_redirect',
        name='courses_slug_redirect'),

    url(r'^(?P<course_id>[\d]+)/signup/',
        'courses.views.course_signup',
        name='courses_signup'),

    url(r'^(?P<course_id>[\d]+)/change_status/(?P<status>draft|publish|archive)/$',
        'courses.views.course_change_status',
        name='courses_change_status'),

    url(r'^(?P<course_id>[\d]+)/change_signup/(?P<signup>open|moderated|closed)/$',
        'courses.views.course_change_signup',
        name='courses_change_signup'),

    url(r'^(?P<course_id>[\d]+)/change_term/(?P<term>fixed|rolling)/$',
        'courses.views.course_change_term',
        name='courses_change_term'),

    url(r'^(?P<course_id>[\d]+)/(?P<slug>[\w-]+)/$',
        'courses.views.show_course',
        name='courses_show'),

    url(r'^(?P<course_id>[\d]+)/remove/(?P<username>[\w\-\.]+)/$',
        'courses.views.course_leave',
        name='courses_leave'),

    url(r'^(?P<course_id>[\d]+)/add_organizer/(?P<username>[\w\-\.]+)/$',
        'courses.views.course_add_organizer',
        name='courses_add_organizer'),

    url(r'^(?P<course_id>[\d]+)/content/create/$',
        'courses.views.create_content',
        name='courses_create_content'),

    url(r'^(?P<course_id>[\d]+)/content/(?P<content_id>[\d]+)/$',
        'courses.views.show_content',
        name='courses_content_show'),
    
    url(r'^(?P<course_id>[\d]+)/content/(?P<content_id>[\d]+)/edit/$',
        'courses.views.edit_content',
        name='courses_edit_content'),

    url(r'^(?P<course_id>[\d]+)/content/(?P<content_id>[\d]+)/up/$',
        'courses.views.content_up',
        name='courses_content_up'),

    url(r'^(?P<course_id>[\d]+)/content/(?P<content_id>[\d]+)/down/$',
        'courses.views.content_down',
        name='courses_content_down'),

    url(r'^(?P<course_id>[\d]+)/content/(?P<content_id>[\d]+)/comment/$',
        'courses.views.post_content_comment',
        name='courses_post_content_comment'),

    url(r'^(?P<course_id>[\d]+)/content/(?P<content_id>[\d]+)/comment/(?P<comment_id>[\d]+)/reply/$',
        'courses.views.post_comment_reply',
        name='courses_post_comment_reply'),

)
