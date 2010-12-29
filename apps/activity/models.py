from django.db import models
from drumbeat.models import ModelBase


class RemoteObject(models.Model):
    """Represents an object originating from another system."""
    object_type = models.URLField(verify_exists=False)
    link = models.ForeignKey('links.Link')
    title = models.CharField(max_length=255)
    uri = models.URLField(null=True)
    created_on = models.DateTimeField(auto_now_add=True)


class Activity(ModelBase):
    """Represents a single activity entry."""
    actor = models.ForeignKey('users.UserProfile')
    verb = models.URLField(verify_exists=False)
    status = models.ForeignKey('statuses.Status', null=True)
    project = models.ForeignKey('projects.Project', null=True)
    target_user = models.ForeignKey('users.UserProfile', null=True,
                                    related_name='target_user')
    remote_object = models.ForeignKey(RemoteObject, null=True)
    parent = models.ForeignKey('self', null=True)
    created_on = models.DateTimeField(auto_now_add=True)
