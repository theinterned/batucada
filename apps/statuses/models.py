from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.utils.timesince import timesince

from projects.models import Project


class Status(models.Model):
    author = models.ForeignKey(User)
    project = models.ForeignKey(Project, null=True)

    object_type = 'http://activitystrea.ms/schema/1.0/status'

    status = models.CharField(max_length=1024)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.status

    @models.permalink
    def get_absolute_url(self):
        return ('statuses_show', (), {
            'status_id': self.pk,
        })

    def timesince(self, now=None):
        return timesince(self.timestamp, now)

admin.site.register(Status)


def status_creation_handler(sender, **kwargs):
    status = kwargs.get('instance', None)
    if not isinstance(status, Status):
        return
    try:
        import activity
        activity.send(status.author, 'post', status, target=status.project)
    except ImportError:
        return

post_save.connect(status_creation_handler, sender=Status)
