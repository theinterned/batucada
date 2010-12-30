from django.db import models
from django.utils.translation import ugettext_lazy as _

from drumbeat.models import ModelBase
from activity import schema


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

    @models.permalink
    def get_absolute_url(self):
        return ('activity_index', (), {
            'activity_id': self.pk,
        })

    def __unicode__(self):
        if self.target_user and self.verb == schema.verbs['follow']:
            return "%s %s %s" % (
                self.actor.name, schema.past_tense['follow'],
                self.target_user.name)
        if self.status:
            return self.status.status
        elif self.remote_object:
            return self.remote_object.title
        return _("%s activity performed by %s") % (self.verb, self.actor.name)
