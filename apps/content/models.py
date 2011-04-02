import logging
import bleach
import datetime

from django.db import models
from django.template.defaultfilters import slugify
from django.contrib import admin
from django.db.models.signals import pre_save, post_save
from django.template.defaultfilters import truncatewords_html
from django.utils.safestring import mark_safe
from django.utils.timesince import timesince
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

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
    slug = models.SlugField()
    content = models.TextField()
    author = models.ForeignKey('users.UserProfile', related_name='pages')
    last_update = models.DateTimeField(auto_now_add=True, default=datetime.datetime.now)
    project = models.ForeignKey('projects.Project', related_name='pages')
    listed = models.BooleanField(default=True)
    collaborative = models.BooleanField(default=True)

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('page_show', (), {
            'slug': self.project.slug,
            'page_slug': self.slug,
        })

    def save(self):
        """Make sure each page has a unique url."""
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
        return mark_safe(_('Added content page'))

    def representation(self):
        return mark_safe('<a href="%s">%s</a>' % (self.get_absolute_url(), self.title))

    def can_edit(self, user):
        if user.is_authenticated():
            profile = user.get_profile()
            if self.collaborative:
                is_participating = self.project.participants().filter(user__pk=profile.pk).exists()
                return (profile == self.project.created_by or is_participating)
            else:
                return (profile == self.project.created_by)
        else:
            return False


admin.site.register(Page)


class PageVersion(ModelBase):

    title = models.CharField(max_length=100)
    content = models.TextField()
    author = models.ForeignKey('users.UserProfile', related_name='page_versions')
    date = models.DateTimeField()
    page = models.ForeignKey('content.Page', related_name='page_versions')

    @models.permalink
    def get_absolute_url(self):
        return ('page_version', (), {
            'slug': self.page.project.slug,
            'page_slug': self.page.slug,
            'version_id': self.id,
        })

admin.site.register(PageVersion)


class PageComment(ModelBase):
    """Placeholder model for comments."""
    object_type = 'http://activitystrea.ms/schema/1.0/comment'

    content = models.TextField()
    author = models.ForeignKey('users.UserProfile', related_name='comments')
    page = models.ForeignKey('content.Page', related_name='comments')
    created_on = models.DateTimeField(
        auto_now_add=True, default=datetime.datetime.now)

    def __unicode__(self):
        return _('Comment to page %s') % self.page.title

    def get_absolute_url(self):
        return reverse('page_show', kwargs={
            'slug': self.project.slug,
            'page_slug': self.page.slug,
        }) + '#%s' % self.id

    def timesince(self, now=None):
        return timesince(self.created_on, now)

    def friendly_verb(self):
        return mark_safe(_('Posted comment'))

    def representation(self):
        return mark_safe(' at <a href="%s">%s</a> page' % (self.get_absolute_url(), self.page.title))

    @property
    def project(self):
        return self.page.project

admin.site.register(PageComment)


###########
# Signals #
###########


def clean_html(sender, **kwargs):
    instance = kwargs.get('instance', None)
    if isinstance(instance, Page) or isinstance(instance, PageComment):
        log.debug("Cleaning html.")
        if instance.content:
            instance.content = bleach.clean(instance.content,
                tags=TAGS, attributes=ALLOWED_ATTRIBUTES,
                styles=ALLOWED_STYLES)

pre_save.connect(clean_html, sender=Page)
pre_save.connect(clean_html, sender=PageComment)


def fire_activity(sender, **kwargs):
    instance = kwargs.get('instance', None)
    created = kwargs.get('created', False)

    if created and (isinstance(instance, Page) or isinstance(instance, PageComment)):
        # fire activity
        activity = Activity(
            actor=instance.author,
            verb='http://activitystrea.ms/schema/1.0/post',
            target_object=instance,
        )
        activity.target_project = instance.project
        activity.save()
        # Send notifications.
        activity.target_project.send_update_notification(activity)

post_save.connect(fire_activity, sender=Page)
post_save.connect(fire_activity, sender=PageComment)

