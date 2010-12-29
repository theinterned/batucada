import datetime

from django.contrib import admin
from django.db import models
from django.db.models import Count
from django.db.models.signals import post_save
from django.template.defaultfilters import slugify

from drumbeat.models import ModelBase
from statuses.models import Status
from relationships.models import Relationship

import caching.base


class ProjectManager(caching.base.CachingManager):
    def get_popular(self, limit=0):
        statuses = Status.objects.values('project_id').annotate(
            Count('id')).exclude(project__isnull=True).filter(
                project__featured=False).order_by('-id__count')[:limit]
        project_ids = [s['project_id'] for s in statuses]
        return Project.objects.filter(id__in=project_ids)


class Project(ModelBase):
    """Placeholder model for projects."""
    object_type = 'http://drumbeat.org/activity/schema/1.0/project'
    generalized_object_type = 'http://activitystrea.ms/schema/1.0/group'
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    call_to_action = models.TextField()
    created_by = models.ForeignKey('users.UserProfile',
                                   related_name='projects')
    featured = models.BooleanField()
    template = models.TextField()
    css = models.TextField()
    created_on = models.DateTimeField(
        auto_now_add=True, default=datetime.date.today())

    objects = ProjectManager()

    def followers(self):
        """Return a list of users following this project."""
        relationships = Relationship.objects.select_related(
            'source').filter(target_project=self)
        return [rel.source for rel in relationships]

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('projects_show', (), {
            'slug': self.slug,
        })

    def save(self):
        """Make sure each project has a unique slug."""
        count = 1
        slug = slugify(self.name)
        self.slug = slug
        while True:
            existing = Project.objects.filter(slug=self.slug)
            if len(existing) == 0:
                break
            self.slug = slug + str(count)
            count += 1
        super(Project, self).save()


admin.site.register(Project)

###########
# Signals #
###########


def project_creation_handler(sender, **kwargs):
    project = kwargs.get('instance', None)
    created = kwargs.get('created', False)

    if not created or not isinstance(project, Project):
        return

    Relationship(source=project.created_by,
                 target_project=project).save()

    try:
        from activity.models import Activity
        act = Activity(actor=project.created_by,
                       verb='http://activitystrea.ms/schema/1.0/post',
                       project=project)
        act.save()
    except ImportError:
        return

post_save.connect(project_creation_handler, sender=Project)
