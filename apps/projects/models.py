from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save

import activity

try:
    from l10n.urlresolvers import reverse
except ImportError:
    from django.core.urlresolvers import reverse
    
class Project(models.Model):
    """Placeholder model for projects."""
    object_type = 'http://drumbeat.org/activity/schema/1.0/project'
    generalized_object_type = 'http://activitystrea.ms/schema/1.0/group'
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_by = models.ForeignKey(User, related_name='projects')

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('projects.views.show', kwargs=dict(project=self.name))

def project_creation_handler(sender, **kwargs):
    project = kwargs.get('instance', None)
    if not isinstance(project, Project):
        return
    activity.send(project.created_by, 'create', project)

post_save.connect(project_creation_handler, sender=Project)
