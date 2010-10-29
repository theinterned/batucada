from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save
from django.template.defaultfilters import slugify

from relationships.models import followers

class Project(models.Model):
    """Placeholder model for projects."""
    object_type = 'http://drumbeat.org/activity/schema/1.0/project'
    generalized_object_type = 'http://activitystrea.ms/schema/1.0/group'
    
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    call_to_action = models.TextField()
    created_by = models.ForeignKey(User, related_name='projects')

    featured = models.BooleanField()
    template = models.TextField()
    css = models.TextField()
    
    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('projects_show', (), {
            'slug': self.slug
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

Project.followers = followers

class Link(models.Model):
    title = models.CharField(max_length=250)
    url = models.URLField()
    project = models.ForeignKey(Project)
    
def project_creation_handler(sender, **kwargs):
    project = kwargs.get('instance', None)
    if not isinstance(project, Project):
        return
    try:
        import activity
        activity.send(project.created_by, 'create', project)
    except ImportError:
        return

post_save.connect(project_creation_handler, sender=Project)
