import logging
import bleach
import datetime

from django.conf import settings
from django.db import models
from django.template.defaultfilters import slugify
from django.contrib import admin
from django.db.models.signals import pre_save, post_save
from django.template.defaultfilters import truncatewords_html
from django.utils.safestring import mark_safe
from django.utils.timesince import timesince
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.db.models import Max
from django.template.loader import render_to_string
from django.contrib.sites.models import Site

from drumbeat.models import ModelBase
from activity.models import Activity
from users.tasks import SendUserEmail

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
    editable = models.BooleanField(default=True)
    index = models.IntegerField()

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
        if not self.index:
            if self.listed:
                max_index = Page.objects.filter(project=self.project, listed=True).aggregate(Max('index'))['index__max']
                self.index = max_index + 1 if max_index else 1
            else:
                self.index = 0
        super(Page, self).save()

    def timesince(self, now=None):
        return timesince(self.created_on, now)

    def friendly_verb(self):
        return mark_safe(_('Added'))

    def representation(self):
        return mark_safe('<a href="%s">%s</a>.' % (self.get_absolute_url(), self.title))

    def can_edit(self, user):
        if not self.editable:
            return False
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
    reply_to = models.ForeignKey('content.PageComment', blank=True, null=True, related_name='replies')
    abs_reply_to = models.ForeignKey('content.PageComment', blank=True, null=True, related_name='all_replies')

    def __unicode__(self):
        return _('Comment to %s') % self.page.title

    def get_absolute_url(self):
        return reverse('page_show', kwargs={
            'slug': self.project.slug,
            'page_slug': self.page.slug,
        }) + '#%s' % self.id

    @property
    def title(self):
        return _('Comment to %s') % self.page.title

    def timesince(self, now=None):
        return timesince(self.created_on, now)

    def friendly_verb(self):
        return mark_safe(_('Posted comment'))

    def representation(self):
        return mark_safe(' at <a href="%s">%s</a>.' % (self.get_absolute_url(), self.page.title))

    @property
    def project(self):
        return self.page.project

    def send_sign_up_notification(self):
        """Send sign_up notifications."""
        if self.page.slug != 'sign-up':
            return
        project = self.page.project
        subject = _('[p2pu-%(slug)s-signup] Course %(name)s\'s signup page was updated') % {
            'slug': project.slug,
            'name': project.name,
            }
        body = render_to_string("content/emails/sign_up_updated.txt", {
            'comment': self,
            'project': project,
            'domain': Site.objects.get_current().domain,
        })
        recipients = {project.created_by.username: project.created_by}
        if self.reply_to:
            comment = self
            while comment.reply_to:
                comment = comment.reply_to
                recipients[comment.author.username] = comment.author
        for username in recipients:
            if recipients[username] != self.author:
                SendUserEmail.apply_async((recipients[username], subject, body))

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
                tags=settings.TAGS, attributes=settings.ALLOWED_ATTRIBUTES,
                styles=settings.ALLOWED_STYLES)

pre_save.connect(clean_html, sender=Page)
pre_save.connect(clean_html, sender=PageComment)


def fire_activity(sender, **kwargs):
    instance = kwargs.get('instance', None)
    created = kwargs.get('created', False)

    is_page = isinstance(instance, Page)
    is_comment = isinstance(instance, PageComment)
    if created and (is_page or is_comment):
        # Do not fire activities for comments on the sign-up page.
        if is_comment and instance.page.slug == 'sign-up':
            instance.send_sign_up_notification()
            return
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

