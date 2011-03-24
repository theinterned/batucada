import logging
import bleach

from django.db import models
from django.template.defaultfilters import slugify
from django.contrib import admin
from django.db.models.signals import pre_save, post_save
from django.template.defaultfilters import truncatewords_html
from django.utils.safestring import mark_safe
from django.utils.timesince import timesince
from django.utils.translation import ugettext_lazy as _

from drumbeat.models import ModelBase
from activity.models import Activity


TAGS = ('h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a', 'b', 'em', 'i', 'strong',
        'ol', 'ul', 'li', 'hr', 'blockquote', 'p',
        'span', 'pre', 'code', 'img',
        'u', 'strike', 'sub', 'sup', 'address', 'div',
        'table', 'thead', 'tr', 'th', 'caption', 'tbody', 'td', 'br')

ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title'],
    'img': ['src', 'alt', 'style', 'title'],
    'p': ['style'],
    'table': ['align', 'border', 'cellpadding', 'cellspacing',
        'style', 'summary'],
    'th': ['scope'],
    'span': ['style'],
    'pre': ['class'],
    'code': ['class'],
}

ALLOWED_STYLES = ['text-align', 'margin-left', 'border-width',
    'border-style', 'margin', 'float', 'width', 'height',
    'font-family', 'font-size', 'color', 'background-color']

log = logging.getLogger(__name__)


class Page(ModelBase):
    """Placeholder model for pages."""
    object_type = 'http://activitystrea.ms/schema/1.0/article'

    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    listed = models.BooleanField(default=True)
    author = models.ForeignKey('users.UserProfile', related_name='pages')
    project = models.ForeignKey('projects.Project', related_name='pages')

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('page_show', (), {
            'slug': self.project.slug,
            'page_slug': self.slug,
        })

    def save(self):
        """Make sure each project has a unique slug."""
        count = 1
        if not self.slug:
            slug = slugify(self.title)
            self.slug = slug
            while True:
                existing = Page.objects.filter(project__slug=self.project.slug, slug=self.slug)
                if len(existing) == 0:
                    break
                self.slug = "%s-%s" % (slug, count + 1)
                count += 1
        super(Page, self).save()

    def timesince(self, now=None):
        return timesince(self.created_on, now)

    def friendly_verb(self):
        return mark_safe(_('Added content'))

    def representation(self):
        return mark_safe('<a href="%s">%s</a>' % (self.get_absolute_url(), self.title))

admin.site.register(Page)


###########
# Signals #
###########


def clean_html(sender, **kwargs):
    page = kwargs.get('instance', None)
    if not isinstance(page, Page):
        return
    log.debug("Cleaning page html.")
    if page.content:
        page.content = bleach.clean(page.content,
            tags=TAGS, attributes=ALLOWED_ATTRIBUTES,
            styles=ALLOWED_STYLES)

pre_save.connect(clean_html, sender=Page)


def fire_new_page_activity(sender, **kwargs):
    page = kwargs.get('instance', None)
    created = kwargs.get('created', False)

    if not created or not isinstance(page, Page):
        return

    # fire activity
    activity = Activity(
        actor=page.author,
        verb='http://activitystrea.ms/schema/1.0/post',
        target_object=page,
    )
    activity.target_project = page.project
    activity.save()

post_save.connect(fire_new_page_activity, sender=Page)

