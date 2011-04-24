import logging
import bleach

from django.db import models
from django.conf import settings
from django.db.models.signals import pre_save
from django.template.defaultfilters import slugify

from drumbeat.models import ModelBase


log = logging.getLogger(__name__)


class School(ModelBase):
    """Placeholder model for schools."""

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('school_home', (), {
            'slug': self.slug,
        })

    def save(self):
        """Make sure each school has a unique slug."""
        count = 1
        if not self.slug:
            slug = slugify(self.name)
            self.slug = slug
            while True:
                existing = School.objects.filter(slug=self.slug)
                if len(existing) == 0:
                    break
                self.slug = "%s-%s" % (slug, count + 1)
                count += 1
        super(School, self).save()


def clean_html(sender, **kwargs):
    instance = kwargs.get('instance', None)
    if isinstance(instance, School):
        log.debug("Cleaning html.")
        if instance.description:
            instance.description = bleach.clean(instance.description,
                tags=settings.RICH_ALLOWED_TAGS, attributes=settings.RICH_ALLOWED_ATTRIBUTES,
                styles=settings.RICH_ALLOWED_STYLES, strip=True)

pre_save.connect(clean_html, sender=School)


