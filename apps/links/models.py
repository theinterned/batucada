import logging

from django.db import models
from django.db.models.signals import post_save, post_delete

from django_push.subscriber.models import Subscription
from django_push.subscriber.signals import updated

from links import tasks

log = logging.getLogger(__name__)


class Link(models.Model):
    name = models.CharField(max_length=100)
    url = models.URLField(max_length=1023)
    project = models.ForeignKey('projects.Project', null=True)
    user = models.ForeignKey('users.UserProfile', null=True)
    subscription = models.ForeignKey(Subscription, null=True)


def link_create_handler(sender, **kwargs):
    link = kwargs.get('instance', None)
    created = kwargs.get('created', False)

    if not created or not isinstance(link, Link):
        return

    tasks.SubscribeToFeed.apply_async(args=(link,))


def link_delete_handler(sender, **kwargs):
    link = kwargs.get('instance', None)

    if not isinstance(link, Link):
        return

    if not link.subscription:
        return

    tasks.UnsubscribeFromFeed.apply_async(args=(link,))

post_save.connect(link_create_handler, sender=Link)
post_delete.connect(link_delete_handler, sender=Link)


def listener(notification, **kwargs):
    sender = kwargs.get('sender', None)
    if not sender:
        return
    tasks.HandleNotification.apply_async(args=(notification, sender))

updated.connect(listener)
