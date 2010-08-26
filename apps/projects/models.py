from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save

from activity import action

class Project(models.Model):
    """Placeholder model for projects."""
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_by = models.ForeignKey(User, related_name='projects')

    def __unicode__(self):
        return self.name

def project_creation_handler(sender, **kwargs):
    project = kwargs.get('instance', None)
    if not isinstance(project, Project):
        return
    action.send(project.created_by, 'create', project)

post_save.connect(project_creation_handler, sender=Project)
