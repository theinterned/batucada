from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.template.loader import render_to_string
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.safestring import mark_safe

from drumbeat.models import ModelBase, ManagerBase
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


class ActivityManager(ManagerBase):

    def public(self):
        """Get list of activities to show on splash page."""

        return Activity.objects.filter(deleted=False,
            parent__isnull=True, remote_object__isnull=True,
            status__isnull=True).filter(
                models.Q(scope_object__isnull=True)
                | models.Q(scope_object__not_listed=False)
            ).exclude(
                verb=schema.verbs['follow']
            ).order_by('-created_on')[:10]

    def dashboard(self, user):
        """
        Given a user, return a list of activities to show on their dashboard.
        """
        projects_following = user.following(model='Project')
        users_following = user.following()
        project_ids = [p.pk for p in projects_following]
        user_ids = [u.pk for u in users_following]
        return Activity.objects.filter(deleted=False).select_related(
            'actor', 'status', 'target_object', 'remote_object',
            'remote_object__link', 'scope_object').filter(
            models.Q(actor__exact=user) | models.Q(actor__in=user_ids)
          | models.Q(scope_object__in=project_ids),
        ).exclude(
            models.Q(verb=schema.verbs['follow']),
            models.Q(scope_object__in=project_ids),
        ).exclude(
            models.Q(verb=schema.verbs['follow']),
            models.Q(actor=user),
        ).exclude(parent__isnull=False).exclude(
            models.Q(status__in_reply_to__isnull=False),
        ).order_by('-created_on')

    def for_user(self, user):
        """Return a list of activities where the actor is user."""
        return Activity.objects.filter(deleted=False).select_related(
            'actor', 'status', 'target_object').filter(
            actor=user).filter(
            models.Q(scope_object__isnull=True)
            | models.Q(scope_object__not_listed=False)
        ).exclude(
            models.Q(verb=schema.verbs['follow']),
            models.Q(scope_object__isnull=True),
        ).exclude(
            models.Q(status__in_reply_to__isnull=False),
        ).order_by('-created_on')[0:25]


class Activity(ModelBase):
    """Represents a single activity entry."""
    actor = models.ForeignKey('users.UserProfile')
    verb = models.URLField(verify_exists=False)
    status = models.ForeignKey('statuses.Status', null=True,
        related_name='activity')
    target_content_type = models.ForeignKey(ContentType, null=True)
    target_id = models.PositiveIntegerField(null=True)
    target_object = generic.GenericForeignKey('target_content_type',
        'target_id')
    scope_object = models.ForeignKey('projects.Project', null=True)
    remote_object = models.ForeignKey(RemoteObject, null=True)
    parent = models.ForeignKey('self', null=True, related_name='comments')
    created_on = models.DateTimeField(auto_now_add=True)
    deleted = models.BooleanField(default=False)

    objects = ActivityManager()

    class Meta:
        verbose_name_plural = _('activities')

    @models.permalink
    def get_absolute_url(self):
        return ('activity_index', (), {
            'activity_id': self.pk,
        })

    @property
    def object_type(self):
        obj = (self.status or self.remote_object
            or self.target_object or None)
        return obj and obj.object_type or None

    @property
    def object_url(self):
        obj = (self.status or self.remote_object
            or self.target_object or None)
        return obj and obj.get_absolute_url() or None

    def textual_representation(self):
        if self.status:
            return self.status.status[:50]
        elif self.remote_object:
            return self.remote_object.title
        elif self.target_object:
            return _('%(actor)s %(verb)s %(target)s') % dict(
                actor=self.actor, verb=self.friendly_verb(),
                target=self.target_object)
        friendly_verb = schema.verbs_by_uri[self.verb]
        return ugettext('%(verb)s activity performed by %(actor)s') % dict(
            verb=friendly_verb, actor=self.actor)

    def friendly_verb(self):
        if self.target_object:
            verb = None
            if hasattr(self.target_object, 'friendly_verb'):
                verb = self.target_object.friendly_verb(self.verb)
            verb = verb or schema.past_tense[schema.verbs_by_uri[self.verb]]
            return verb
        if self.verb == schema.verbs['post']:
            comment_type = schema.object_types['comment']
            if self.object_type == comment_type:
                return mark_safe(ugettext('posted comment'))
            else:
                return mark_safe(ugettext('added'))
        else:
            return schema.past_tense[schema.verbs_by_uri[self.verb]]

    def html_representation(self):
        return render_to_string('activity/_activity_body.html', {
            'activity': self,
            'show_actor': True,
        })

    def __unicode__(self):
        return _("Activity ID %(id)d. Actor id %(actor)d, Verb %(verb)s") % {
            'id': self.pk, 'actor': self.actor.pk, 'verb': self.verb}

    def can_edit(self, user):
        if not self.status:
            return False
        if user.is_authenticated():
            profile = user.get_profile()
            return (profile == self.actor)
        else:
            return False
