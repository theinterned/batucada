import datetime

from django.db import models

from projects.models import Link


class Entry(models.Model):
    link = models.ForeignKey(Link, related_name='feed_entries')
    signature = models.CharField(max_length=32)
    created_on = models.DateTimeField(
        auto_now_add=True, default=datetime.date.today())


class RemoteObject(models.Model):
    title = models.CharField(max_length=255)
    url = models.URLField()
    created_on = models.DateTimeField(
        auto_now_add=True, default=datetime.date.today())

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return self.url
