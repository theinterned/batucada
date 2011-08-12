import logging
import datetime

from django.db import models
from django.template.defaultfilters import slugify
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _
from django.db.models import Max
from django.contrib.sites.models import Site
from django.contrib.contenttypes import generic
from django.conf import settings

from drumbeat.models import ModelBase
from activity.models import Activity
from activity.schema import verbs, object_types
from users.tasks import SendUserEmail
from l10n.models import localize_email
from richtext.models import RichTextField
from replies.models import PageComment


log = logging.getLogger(__name__)


class Page(ModelBase):
    """Placeholder model for pages."""
    object_type = object_types['article']

    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=110)
    content = RichTextField(config_name='rich', blank='False')
    author = models.ForeignKey('users.UserProfile', related_name='pages')
    last_update = models.DateTimeField(auto_now_add=True,
        default=datetime.datetime.now)
    project = models.ForeignKey('projects.Project', related_name='pages')
    listed = models.BooleanField(default=True)
    minor_update = models.BooleanField(default=True)
    collaborative = models.BooleanField(default=True)
    index = models.IntegerField()
    deleted = models.BooleanField(default=False)

    comments = generic.GenericRelation(PageComment,
        content_type_field='page_content_type',
        object_id_field='page_id')

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('page_show', (), {
            'slug': self.project.slug,
            'page_slug': self.slug,
        })

    def friendly_verb(self, verb):
        if verbs['post'] == verb:
            return _('added')

    def save(self):
        """Make sure each page has a unique url."""
        count = 1
        if not self.slug:
            slug = slugify(self.title)
            self.slug = slug
            while True:
                existing = Page.objects.filter(
                    project__slug=self.project.slug, slug=self.slug)
                if len(existing) == 0:
                    break
                self.slug = "%s-%s" % (slug, count + 1)
                count += 1
        if not self.index:
            if self.listed:
                max_index = Page.objects.filter(project=self.project,
                    listed=True).aggregate(Max('index'))['index__max']
                self.index = max_index + 1 if max_index else 1
            else:
                self.index = 0
        super(Page, self).save()

    def can_edit(self, user):
        if self.project.is_organizing(user):
            return True
        if self.collaborative:
            return self.project.is_participating(user)
        return False

    def first_level_comments(self):
        return self.comments.filter(reply_to__isnull=True).order_by(
            '-created_on')

    def can_comment(self, user, reply_to=None):
        return self.project.is_participating(user)

    def get_comment_url(self, comment, user):
        comment_index = 0
        abs_reply_to = comment.abs_reply_to or comment
        for first_level_comment in self.first_level_comments():
            if abs_reply_to.id == first_level_comment.id:
                break
            comment_index += 1
        items_per_page = settings.PAGINATION_DEFAULT_ITEMS_PER_PAGE
        page = (comment_index / items_per_page) + 1
        url = self.get_absolute_url()
        return url + '?pagination_page_number=%s#%s' % (
            page, comment.id)

    def comments_fire_activity(self):
        return True

    def comment_notification_recipients(self, comment):
        from users.models import UserProfile
        user_ids = self.project.participants().filter(
            no_updates=False).values('user__id')
        return UserProfile.objects.filter(id__in=user_ids)


class PageVersion(ModelBase):

    title = models.CharField(max_length=100)
    content = RichTextField(config_name='rich', blank='False')
    author = models.ForeignKey('users.UserProfile',
        related_name='page_versions')
    date = models.DateTimeField()
    page = models.ForeignKey('content.Page', related_name='page_versions')
    deleted = models.BooleanField(default=False)
    minor_update = models.BooleanField(default=True)

    @models.permalink
    def get_absolute_url(self):
        return ('page_version', (), {
            'slug': self.page.project.slug,
            'page_slug': self.page.slug,
            'version_id': self.id,
        })


def send_email_notification(instance):
    project = instance.project
    if not instance.listed:
        return
    context = {
        'instance': instance,
        'project': project,
        'domain': Site.objects.get_current().domain,
    }
    subjects, bodies = localize_email(
        'content/emails/content_update_subject.txt',
        'content/emails/content_update.txt', context)
    for participation in project.participants():
        is_author = (instance.author == participation.user)
        if not is_author and not participation.no_updates:
            SendUserEmail.apply_async(
                    (participation.user, subjects, bodies))


###########
# Signals #
###########


def fire_activity(sender, **kwargs):
    instance = kwargs.get('instance', None)
    created = kwargs.get('created', False)
    is_page = isinstance(instance, Page)
    if created and is_page:
        send_email_notification(instance)
        # Fire activity.
        activity = Activity(actor=instance.author, verb=verbs['post'],
            target_object=instance, scope_object=instance.project)
        activity.save()
    elif (not created and is_page and not instance.minor_update \
          and not instance.deleted):
        activity = Activity(actor=instance.author, verb=verbs['update'],
            target_object=instance, scope_object=instance.project)
        activity.save()

post_save.connect(fire_activity, sender=Page,
    dispatch_uid='content_page_fire_activity')
