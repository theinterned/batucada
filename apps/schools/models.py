import logging
import bleach

from django.db import models
from django.conf import settings
from django.db.models.signals import pre_save
from django.template.defaultfilters import slugify

from drumbeat.models import ModelBase
from drumbeat.utils import get_partition_id, safe_filename
from drumbeat import storage


log = logging.getLogger(__name__)


def determine_image_upload_path(instance, filename):
    return "images/schools/%(partition)d/%(filename)s" % {
        'partition': get_partition_id(instance.pk),
        'filename': safe_filename(filename),
    }


class School(ModelBase):
    """Placeholder model for schools."""

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    organizers = models.ManyToManyField('users.UserProfile', null=True, blank=True)
    featured = models.ManyToManyField('projects.Project', related_name='school_featured', null=True, blank=True)
    declined = models.ManyToManyField('projects.Project', related_name='school_declined', null=True, blank=True)

    image = models.ImageField(upload_to=determine_image_upload_path, null=True,
                              storage=storage.ImageStorage(), blank=True)
    text_color = models.CharField(max_length=7, default='#5A6579')
    

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


