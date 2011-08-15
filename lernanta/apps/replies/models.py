import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from users.tasks import SendUserEmail
from l10n.models import localize_email
from django.contrib.sites.models import Site

from drumbeat.models import ModelBase
from activity.schema import verbs, object_types

from richtext.models import RichTextField


class PageComment(ModelBase):
    """Placeholder model for comments."""
    object_type = object_types['comment']

    content = RichTextField(config_name='rich', blank=False)
    author = models.ForeignKey('users.UserProfile',
        related_name='comments')

    # the comments can live inside a project, a school, or just be associated
    # with their author
    scope_content_type = models.ForeignKey(ContentType, null=True,
        related_name='scope_page_comments')
    scope_id = models.PositiveIntegerField(null=True)
    scope_object = generic.GenericForeignKey('scope_content_type',
        'scope_id')

    # object to which the comments are associated (a task, a signup answer,
    # an activity on the wall, ...)
    page_content_type = models.ForeignKey(ContentType, null=True)
    page_id = models.PositiveIntegerField(null=True)
    page_object = generic.GenericForeignKey('page_content_type',
        'page_id')

    created_on = models.DateTimeField(
        auto_now_add=True, default=datetime.datetime.now)
    reply_to = models.ForeignKey('replies.PageComment', blank=True,
        null=True, related_name='replies')
    abs_reply_to = models.ForeignKey('replies.PageComment', blank=True,
        null=True, related_name='all_replies')
    deleted = models.BooleanField(default=False)

    def __unicode__(self):
        return _('comment at %s') % self.page_object

    @models.permalink
    def get_absolute_url(self):
        return ('comment_show', (), {
            'comment_id': self.id,
        })

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

    def send_comment_notification(self):
        context = {
            'comment': self,
            'domain': Site.objects.get_current().domain,
        }
        subjects, bodies = localize_email(
            'replies/emails/post_comment_subject.txt',
            'replies/emails/post_comment.txt', context)
        recipients = self.page_object.comment_notification_recipients(self)
        for recipient in recipients:
            if self.author != recipient:
                SendUserEmail.apply_async((recipient, subjects, bodies))


###########
# Signals #
###########

def fire_activity(sender, **kwargs):
    instance = kwargs.get('instance', None)
    created = kwargs.get('created', False)
    is_comment = isinstance(instance, PageComment)
    if created and is_comment:
        instance.send_comment_notification()
        if instance.page_object.comments_fire_activity():
            from activity.models import Activity
            activity = Activity(actor=instance.author, verb=verbs['post'],
                target_object=instance, scope_object=instance.scope_object)
            activity.save()


post_save.connect(fire_activity, sender=PageComment,
    dispatch_uid='replies_pagecomment_fire_activity')
