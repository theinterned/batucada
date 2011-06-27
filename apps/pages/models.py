import logging

from django.conf import settings
from django.db import models

from drumbeat.models import ModelBase

log = logging.getLogger(__name__)


class Page(ModelBase):
    """Model for static pages."""

    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=110)
    content = models.TextField()
    language = models.CharField(verbose_name='language',
        max_length=16, choices=settings.SUPPORTED_LANGUAGES,
        default=settings.LANGUAGE_CODE)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("slug", "language"),)

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('static_page_show', (), {
            'slug': self.slug,
        })
