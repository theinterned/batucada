import datetime
from markdown import markdown
import bleach

from django.db import models
from django.db.models.signals import post_save
from django.utils.timesince import timesince
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from django.conf import settings

from activity.models import Activity
from drumbeat.models import ModelBase
from users.tasks import SendUserEmail

class Status(ModelBase):
    object_type = 'http://activitystrea.ms/schema/1.0/status'

    author = models.ForeignKey('users.UserProfile')
    project = models.ForeignKey('projects.Project', null=True, blank=True)
    status = models.TextField()
    created_on = models.DateTimeField(
        auto_now_add=True, default=datetime.datetime.now)
    important = models.BooleanField(default=False)

    def __unicode__(self):
        return self.status

    def get_absolute_url(self):
        return self.activity.get().get_absolute_url()

    def timesince(self, now=None):
        return timesince(self.created_on, now)

    def send_wall_notification(self):
        """Send update notifications for messages posted to a study group wall."""
        if not self.project:
            return
        project = self.project
        subject = render_to_string("statuses/emails/wall_updated_subject.txt", {
            'status': self,
            'project': project,
        })
        body = render_to_string("statuses/emails/wall_updated.txt", {
            'status': self,
            'project': project,
            'domain': Site.objects.get_current().domain,
        })
        for participation in project.participants():
            if (not self.important and participation.no_wall_updates) or self.author == participation.user:
                continue
            SendUserEmail.apply_async((participation.user, subject, body))
        if self.author != project.created_by:
            SendUserEmail.apply_async((self.author, subject, body))


###########
# Signals #
###########


def status_creation_handler(sender, **kwargs):
    status = kwargs.get('instance', None)
    created = kwargs.get('created', False)

    if not created or not isinstance(status, Status):
        return

    # clean html
    status.status = bleach.clean(status.status, tags=settings.REDUCED_ALLOWED_TAGS, attributes=settings.REDUCED_ALLOWED_ATTRIBUTES, strip=True)
    status.save()

    # fire activity
    activity = Activity(
        actor=status.author,
        verb='http://activitystrea.ms/schema/1.0/post',
        status=status,
    )
    if status.project:
        activity.target_project = status.project
    activity.save()
    # Send notifications.
    if status.project:
        status.send_wall_notification()
post_save.connect(status_creation_handler, sender=Status)
