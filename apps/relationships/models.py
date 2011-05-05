import datetime
import logging

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import activate, get_language, ugettext
from django.template.loader import render_to_string
from django.contrib.sites.models import Site

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
        auto_now_add=True, default=datetime.datetime.now)

    def save(self, *args, **kwargs):
        """Check that the source and the target are not the same user."""
        if (self.source == self.target_user):
            raise ValidationError(
                _('Cannot create self referencing relationship.'))
        super(Relationship, self).save(*args, **kwargs)

    class Meta:
        unique_together = (
            ('source', 'target_user'),
            ('source', 'target_project'),
        )

    def __unicode__(self):
        return "%(from)r => %(to)r" % {
            'from': repr(self.source),
            'to': repr(self.target_user or self.target_project),
        }

###########
# Signals #
###########


def follow_handler(sender, **kwargs):
    rel = kwargs.get('instance', None)
    created = kwargs.get('created', False)
    if not created or not isinstance(rel, Relationship):
        return
    user_subject = ugettext('%(display_name)s is following you on P2PU!') % {
        'display_name': rel.source.display_name,
    }
    project_subject = ugettext('%(display_name)s is following %(project)s on P2PU!') % {
        'display_name': rel.source.display_name,
        'project': rel.target_project,
    }
    activity = Activity(actor=rel.source,
                        verb='http://activitystrea.ms/schema/1.0/follow')
    subject = ugettext('%(display_name)s is now following')
    if rel.target_user:
        activity.target_user = rel.target_user
        user = rel.target_user
        pref_key = 'no_email_new_follower'
        subject = user_subject
    else:
        activity.project = rel.target_project
        user = rel.target_project.created_by
        pref_key = 'no_email_new_project_follower'
        subject = project_subject
    activity.save()

    preferences = AccountPreferences.objects.filter(user=user)
    for pref in preferences:
        if pref.value and pref.key == pref_key:
            return
    ulang=get_language()
    activate(user.preflang or settings.LANGUAGE_CODE)
    body = render_to_string("relationships/emails/new_follower.txt", {
        'user': rel.source,
        'project': rel.target_project,
        'domain': Site.objects.get_current().domain,
    })
    activate(ulang)
    SendUserEmail.apply_async((user, subject, body))
post_save.connect(follow_handler, sender=Relationship)
