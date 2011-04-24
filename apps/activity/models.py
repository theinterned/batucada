from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.template.loader import render_to_string
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

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
    status = models.ForeignKey('statuses.Status', null=True, related_name='activity')
    target_content_type = models.ForeignKey(ContentType, null=True)
    target_id = models.PositiveIntegerField(null=True)
    target_object = generic.GenericForeignKey('target_content_type', 'target_id')
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
        obj = (self.status or self.target_user or self.remote_object 
        or self.target_object or None)
        return obj and obj.object_type or None

    @property
    def object_url(self):
        obj = (self.status or self.target_user or self.remote_object 
        or self.target_object or None)
        return obj and obj.get_absolute_url() or None

    def textual_representation(self):
        target = self.target_user or self.target_project or self.project
        if target and self.verb == schema.verbs['follow']:
            return _('%(actor)s %(verb)s %(target)s') % dict(
                actor=self.actor.display_name, verb=schema.past_tense['follow'],
                target=target.name)
        if self.status:
            return self.status.status
        elif self.remote_object:
            return self.remote_object.title

        elif self.target_object:
            return self.target_object.title

        friendly_verb = schema.verbs_by_uri[self.verb]
        return ugettext('%(verb)s activity performed by %(actor)s') % dict(verb=friendly_verb,
                                                   actor=self.actor.display_name)

    def html_representation(self):
        return render_to_string('activity/_activity_body.html', {
            'activity': self,
            'show_actor': True,
        })

    def __unicode__(self):
        return _("Activity ID %(self.pk)d. Actor id %(self.actor.pk)d, Verb %(self.verb)s") % (
            self.pk, self.actor.pk, self.verb)
