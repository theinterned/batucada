from django.db import models

from projects.models import Link


class Entry(models.Model):
    link = models.ForeignKey(Link, related_name='feed_entries')
    processed_on = models.DateTimeField(auto_now_add=True)
