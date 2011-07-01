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
                models.Q(target_project__isnull=True)
                | models.Q(target_project__not_listed=False),
                models.Q(project__isnull=True)
                | models.Q(project__not_listed=False)
            ).exclude(
                verb='http://activitystrea.ms/schema/1.0/follow'
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
            'actor', 'status', 'project', 'remote_object',
            'remote_object__link', 'target_project').filter(
            models.Q(actor__exact=user) |
            models.Q(actor__in=user_ids) | models.Q(project__in=project_ids),
        ).exclude(
            models.Q(verb='http://activitystrea.ms/schema/1.0/follow'),
            models.Q(target_user__isnull=True),
            models.Q(project__in=project_ids),
        ).exclude(
            models.Q(verb='http://activitystrea.ms/schema/1.0/follow'),
            models.Q(actor=user),
        ).exclude(parent__isnull=False).exclude(
            models.Q(status__in_reply_to__isnull=False),
        ).order_by('-created_on')

    def for_user(self, user):
        """Return a list of activities where the actor is user."""
        return Activity.objects.filter(deleted=False).select_related(
            'actor', 'status', 'project').filter(
            actor=user).filter(
            models.Q(target_project__isnull=True)
            | models.Q(target_project__not_listed=False),
            models.Q(project__isnull=True)
            | models.Q(project__not_listed=False)
        ).exclude(
            models.Q(verb='http://activitystrea.ms/schema/1.0/follow'),
            models.Q(target_user__isnull=False),
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
    project = models.ForeignKey('projects.Project', null=True)
    target_user = models.ForeignKey('users.UserProfile', null=True,
                                    related_name='target_user')
    target_project = models.ForeignKey('projects.Project', null=True,
                                       related_name='target_project')
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
            name = target if self.target_user else target.name
            return _('%(actor)s %(verb)s %(target)s') % dict(
                actor=self.actor,
                verb=schema.past_tense['follow'], target=name)
        if self.status:
            return self.status.status[:50]
        elif self.remote_object:
            return self.remote_object.title
        elif self.target_object:
            return _('%(actor)s %(verb)s %(target)s') % dict (
                actor=self.actor, verb=self.friendly_verb(), target=self.target_object)
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
            if self.project_id:
                return mark_safe(ugettext('created'))
            else:
                comment_type = 'http://activitystrea.ms/schema/1.0/comment'
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
