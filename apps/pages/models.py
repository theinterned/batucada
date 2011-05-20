import logging

from django.conf import settings
from django.db import models
from django.contrib.sites.models import Site

from drumbeat.models import ModelBase

log = logging.getLogger(__name__)


class Page(ModelBase):
    """Model for static pages."""

    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=110, unique=True)
    content = models.TextField()

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('static_page_show', (), {
            'slug': self.slug,
        })
