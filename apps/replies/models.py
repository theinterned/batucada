import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.db.models.signals import post_save
from django.contrib.sites.models import Site

from drumbeat.models import ModelBase
from activity.schema import verbs, object_types
from activity.models import Activity
from users.tasks import SendUserEmail
from l10n.models import localize_email
from richtext.models import RichTextField
from signups.models import send_sign_up_notification


class PageComment(ModelBase):
    """Placeholder model for comments."""
    object_type = object_types['comment']

    content = RichTextField(config_name='rich', blank='False')
    author = models.ForeignKey('users.UserProfile',
        related_name='comments')
    page = models.ForeignKey('content.Page', related_name='comments')
    created_on = models.DateTimeField(
        auto_now_add=True, default=datetime.datetime.now)
    reply_to = models.ForeignKey('replies.PageComment', blank=True,
        null=True, related_name='replies')
    abs_reply_to = models.ForeignKey('replies.PageComment', blank=True,
        null=True, related_name='all_replies')
    deleted = models.BooleanField(default=False)

    def __unicode__(self):
        if self.page.slug == 'sign-up' and not self.reply_to:
            return _('answer at %s') % self.page.title
        else:
            return _('comment at %s') % self.page.title

    @models.permalink
    def get_absolute_url(self):
        return ('comment_show', (), {
            'slug': self.page.project.slug,
            'page_slug': self.page.slug,
            'comment_id': self.id,
        })

    @property
    def title(self):
        return ugettext('Comment to %s') % self.page.title

    @property
    def project(self):
        return self.page.project

    def has_visible_childs(self):
        return self.visible_replies().exists()

    def visible_replies(self):
        return self.all_replies.filter(deleted=False).order_by('created_on')

    def can_edit(self, user):
        if user.is_authenticated():
            profile = user.get_profile()
            return (profile == self.author)
        else:
            return False


def send_email_notification(instance):
    project = instance.project
    context = {
        'instance': instance,
        'project': project,
        'domain': Site.objects.get_current().domain,
    }
    subjects, bodies = localize_email(
        'replies/emails/post_comment_subject.txt',
        'replies/emails/post_comment.txt', context)
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
    is_comment = isinstance(instance, PageComment)
    if created and is_comment:
        # Send notification.
        if instance.page.slug == 'sign-up':
            send_sign_up_notification(instance)
        else:
            send_email_notification(instance)
        # Fire activity.
        activity = Activity(actor=instance.author, verb=verbs['post'],
            target_object=instance, scope_object=instance.project)
        activity.save()


post_save.connect(fire_activity, sender=PageComment,
    dispatch_uid='replies_pagecomment_fire_activity')
