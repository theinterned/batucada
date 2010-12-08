import datetime

from django.db import models

from projects.models import Link

import caching.base


class Entry(caching.base.CachingMixin, models.Model):
    link = models.ForeignKey(Link, related_name='feed_entries')
    signature = models.CharField(max_length=32)
    created_on = models.DateTimeField(
        auto_now_add=True, default=datetime.date.today())
    objects = caching.base.CachingManager()


class RemoteObject(caching.base.CachingMixin, models.Model):
    title = models.CharField(max_length=255)
    url = models.URLField()
    created_on = models.DateTimeField(
        auto_now_add=True, default=datetime.date.today())
    objects = caching.base.CachingManager()

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return self.url
