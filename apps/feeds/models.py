from django.db import models

from projects.models import Link


class Entry(models.Model):
    link = models.ForeignKey(Link, related_name='feed_entries')
    signature = models.CharField(max_length=32)
    processed_on = models.DateTimeField(auto_now_add=True)


class RemoteObject(models.Model):
    title = models.CharField(max_length=255)
    url = models.URLField()

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return self.url
