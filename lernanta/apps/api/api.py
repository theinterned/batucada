from tastypie.resources import ModelResource
from tastypie import fields
from projects.models import Project
from users.models import UserProfile
from schools.models import School
from badges.models import Badge


class UserProfileResource(ModelResource):
    class Meta:
        queryset = UserProfile.objects.all()
        fields = ['username', 'bio', 'image']


class SchoolResource(ModelResource):
    class Meta:
        queryset = School.objects.all()


class BadgeResource(ModelResource):
    class Meta:
        queryset = Badge.objects.all()


class ProjectResource(ModelResource):
    school = fields.ForeignKey(SchoolResource, 'school', null=True)
    completion_badges = fields.ToManyField(BadgeResource, 'badges', null=True)

    class Meta:
        queryset = Project.objects.get_active()
        fields = ['school', 'category', 'community_featured', 'created_on',
                'duration_hours', 'end_date', 'featured', 'image', 'language',
                'long_description', 'name', 'other', 'other_description',
                'resource_uri', 'short_description', 'slug', 'start_date',
                'completion_badges']
