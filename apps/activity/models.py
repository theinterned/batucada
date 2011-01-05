from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string

from drumbeat.models import ModelBase
from activity import schema


class RemoteObject(models.Model):
    """Represents an object originating from another system."""
    object_type = models.URLField(verify_exists=False)
    link = models.ForeignKey('links.Link')
    title = models.CharField(max_length=255)
    uri = models.URLField(null=True)
    created_on = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return self.uri


class Activity(ModelBase):
    """Represents a single activity entry."""
    actor = models.ForeignKey('users.UserProfile')
    verb = models.URLField(verify_exists=False)
    status = models.ForeignKey('statuses.Status', null=True)
    project = models.ForeignKey('projects.Project', null=True)
    target_user = models.ForeignKey('users.UserProfile', null=True,
                                    related_name='target_user')
    target_project = models.ForeignKey('projects.Project', null=True,
                                       related_name='target_project')
    remote_object = models.ForeignKey(RemoteObject, null=True)
    parent = models.ForeignKey('self', null=True)
    created_on = models.DateTimeField(auto_now_add=True)

    @models.permalink
    def get_absolute_url(self):
        return ('activity_index', (), {
            'activity_id': self.pk,
        })

    @property
    def object_type(self):
        obj = self.status or self.target_user or self.remote_object or None
        return obj and obj.object_type or None

    @property
    def object_url(self):
        obj = self.status or self.target_user or self.remote_object or None
        return obj and obj.get_absolute_url() or None

    def textual_representation(self):
        if self.target_user and self.verb == schema.verbs['follow']:
            return "%s %s %s" % (
                self.actor.name, schema.past_tense['follow'],
                self.target_user.name)
        if self.status:
            return self.status.status
        elif self.remote_object:
            return self.remote_object.title
        return _("%s activity performed by %s") % (self.verb, self.actor.name)

    def html_representation(self):
        return render_to_string('activity/_activity_body.html', {
            'activity': self,
            'show_actor': True,
        })

    def __unicode__(self):
        return _("Activity ID %d. Actor id %d, Verb %s") % (
            self.pk, self.actor.pk, self.verb)
