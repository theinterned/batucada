import urllib2
import logging

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save, post_delete

from django_push.subscriber.models import Subscription
from django_push.subscriber.signals import updated

from links import utils


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

    hub_url = None

    try:
        html = urllib2.urlopen(link.url).read()
        feed_url = utils.parse_feed_url(html)
        feed = urllib2.urlopen(feed_url).read()
        hub_url = utils.parse_hub_url(feed)
    except:
        log.error("Error getting hub URL for %s" % (link.url,))

    if hub_url:
        log.debug("Found hub (%s) for feed (%s). Subscribing" % (
            hub_url, feed_url))
        subscription = Subscription.objects.subscribe(feed_url, hub=hub_url)
        link.subscription = subscription
        link.save()
    else:
        log.debug("Using SuperFeedr to subscribe to feed (%s)" % (
            feed_url,))
        subscription = Subscription.objects.subscribe(
            feed_url,
            hub=settings.SUPERFEEDR_HUB_URL)
        link.subscription = subscription
        link.save()


def link_delete_handler(sender, **kwargs):
    link = kwargs.get('instance', None)

    if not isinstance(link, Link):
        return

    if not link.subscription:
        return

    Subscription.objects.unsubscribe(link.subscription.topic,
                                     hub=link.subscription.hub)

post_save.connect(link_create_handler, sender=Link)
post_delete.connect(link_delete_handler, sender=Link)


def listener(notification, **kwargs):
    import activity
    sender = kwargs.get('sender', None)
    if not sender:
        return
    for entry in notification.entries:
        if isinstance(entry.content, list):
            content = entry.content[0]
            if 'value' in content:
                content = content['value']
        else:
            content = entry.content
        for link in sender.link_set.all():
            activity.send(link.user.user, 'post', {
                'type': 'note',
                'title': entry.title,
                'content': content,
            })
        log.debug("Entry title: %s" % (entry.title,))
        log.debug("Entry link: %s" % (entry.link,))

updated.connect(listener)
