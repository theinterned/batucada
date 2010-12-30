import datetime
import logging

from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import ugettext as _

from drumbeat.models import ModelBase
from activity.models import Activity
from preferences.models import AccountPreferences
from users.tasks import SendUserEmail

log = logging.getLogger(__name__)


class Relationship(ModelBase):
    """
    A relationship between two objects. Source is usually a user but can
    be any ```Model``` instance. Target can also be any ```Model``` instance.
    """
    source = models.ForeignKey(
        'users.UserProfile', related_name='source_relationships')
    target_user = models.ForeignKey(
        'users.UserProfile', null=True, blank=True)
    target_project = models.ForeignKey(
        'projects.Project', null=True, blank=True)

    created_on = models.DateTimeField(
        auto_now_add=True, default=datetime.date.today())

    def save(self, *args, **kwargs):
        """Check that the source and the target are not the same user."""
        if (self.source == self.target_user):
            raise ValidationError(
                _('Cannot create self referencing relationship.'))
        super(Relationship, self).save(*args, **kwargs)

    class Meta:
        unique_together = ('source', 'target_user')

    def __unicode__(self):
        return "%(from)r => %(to)r" % {
            'from': repr(self.source),
            'to': repr(self.target_user or self.target_project),
        }

admin.site.register(Relationship)

###########
# Signals #
###########


def follow_handler(sender, **kwargs):
    rel = kwargs.get('instance', None)
    if not isinstance(rel, Relationship):
        return
    activity = Activity(actor=rel.source,
                        verb='http://activitystrea.ms/schema/1.0/follow')
    if rel.target_user:
        activity.target_user = rel.target_user
        user = rel.target_user
        pref_key = 'no_email_new_follower'
    else:
        activity.project = rel.target_project
        user = rel.target_project.created_by
        pref_key = 'no_email_new_project_follower'
    activity.save()

    preferences = AccountPreferences.objects.filter(user=user)
    for pref in preferences:
        if pref.value and pref.key == pref_key:
            return
    subject = "New Follower"  # todo - write copy
    body = ""
    SendUserEmail.apply_async((user, subject, body))
post_save.connect(follow_handler, sender=Relationship)
