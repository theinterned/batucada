from django.conf.urls.defaults import patterns, url, include


urlpatterns = patterns('',
    url(r'^ckeditor/upload/', 'richtext.views.upload_image',
        name='richtext_upload_image'),
    url(r'^upload/', 'richtext.views.upload_file',
        name='richtext_upload_file'),
    url(r'^browse/', 'richtext.views.browse_file',
        name='richtext_browse_file'),
    (r'^ckeditor/',      include('ckeditor.urls')),
)
