from settings import *

# Useful settings for running a local instance of batucada.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {

    'default': {
        'NAME': 'lernanta',
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'lernanta',
        'PASSWORD': '',
        'HOST': '', # An empty string means localhost.
        'PORT': '', # An empty string means the default port.
        'OPTIONS': {'init_command': 'SET storage_engine=InnoDB'},
    },

    # Comment the following lines to disable drupal user support.
    'drupal_users': {
        'NAME': 'drupal_user_data',
        'TEST_NAME': 'drupal_user_data',
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'drupal_db_user',
        'PASSWORD': '',
        'HOST': '', # An empty string means localhost.
        'PORT': '', # An empty string means the default port.
    }

}

TIME_ZONE = 'America/Toronto'

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}

INSTALLED_APPS += (
    'debug_toolbar',
    'django_nose',
)

MIDDLEWARE_CLASSES += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)
INTERNAL_IPS = ('127.0.0.1',)

# Use dummy caching for development.
CACHE_BACKEND = 'dummy://'
CACHE_PREFIX = 'batucada'
CACHE_COUNT_TIMEOUT = 60

# Execute celery tasks locally, so you don't have to be running an MQ
CELERY_ALWAYS_EAGER = True

# Path to ffmpeg. This will have to be installed to create video thumbnails
FFMPEG_PATH = '/usr/bin/ffmpeg'

# Ckeditor
CKEDITOR_MEDIA_PREFIX = "/media/ckeditor/"
CKEDITOR_UPLOAD_PATH = path("uploads")
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': [
            ['Source'],
            ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript'],
            ['JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            ['NumberedList', 'BulletedList', 'HorizontalRule', 'Outdent', 'Indent', 'SourceCode', 'Blockquote'],
            ['Maximize'],
            ['Link', 'Unlink', 'Image', 'YouTube', 'SlideShare', 'Smiley', 'SpecialChar', 'Table'],
            ['Format','Font','FontSize', 'TextColor','BGColor'],
        ],
        'skin': 'kama',
        'width': '570',
        'height': '255',
        'removePlugins': 'resize, elementspath',
        'toolbarCanCollapse': False,
        'extraPlugins': 'youtube,slideshare,prettify',
        'format_tags': 'p;h1;h2;h3;h4;h5;h6',
        'prettify': { 'element' : 'pre', 'attributes' : { 'class' : 'prettyprint' }},
    },
}

# Set to True at production before upgrading lernanta.
# Remember to login as admin before activating maintenance mode.
MAINTENANCE_MODE = False

