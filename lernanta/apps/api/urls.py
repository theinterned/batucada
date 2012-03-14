from django.conf.urls.defaults import *

from tastypie.api import Api
from apps.api.api import ProjectResource, UserProfileResource, SchoolResource, BadgeResource

v1_api = Api(api_name='v1')
v1_api.register(ProjectResource())
v1_api.register(UserProfileResource())
v1_api.register(SchoolResource())
v1_api.register(BadgeResource())

urlpatterns = patterns('',
    (r'^api/', include(v1_api.urls)),
)
