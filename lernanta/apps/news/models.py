from django.db import models

from drumbeat.models import ModelBase


class FeedEntry(ModelBase):
    title = models.CharField(max_length=255)
    link = models.URLField()
    body = models.TextField()
    page = models.CharField(max_length=50)
    checksum = models.CharField(max_length=32, unique=True)
    created_on = models.DateTimeField()
