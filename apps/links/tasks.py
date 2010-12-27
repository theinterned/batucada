import sys
import urllib2

from django.conf import settings

from celery.task import Task
from django_push.subscriber.models import Subscription

from links import utils

import activity


class SubscribeToFeed(Task):
    """
    Try to discover an Atom or RSS feed for the provided link and
    subscribe to it. Try to discover a hub declaration for the feed.
    If no hub is declared, fall back to using SuperFeedr.
    """

    max_retries = 3

    def run(self, link, **kwargs):
        log = self.get_logger(**kwargs)

        hub_url = None
        feed_url = None

        try:
            log.debug("Attempting feed discovery on %s" % (link.url,))
            html = urllib2.urlopen(link.url).read()
            feed_url = utils.parse_feed_url(html, link.url)
            log.debug("Found feed URL %s for %s" % (feed_url, link.url))
        except:
            log.warning("Error discoverying feed URL for %s. Retrying." % (
                link.url,))
            self.retry([link, ], kwargs)

        if not feed_url:
            return

        try:
            log.debug("Attempting hub discovery on %s" % (feed_url,))
            feed = urllib2.urlopen(feed_url).read()
            hub_url = utils.parse_hub_url(feed, feed_url)
            log.debug("Found hub %s for %s" % (hub_url, feed_url))
        except:
            log.warning("Error discoverying hub URL for %s. Retrying." % (
                feed_url,))
            self.retry([link, ], kwargs)

        try:
            hub = hub_url or settings.SUPERFEEDR_URL
            log.debug("Attempting subscription of topic %s with hub %s" % (
                feed_url, hub))
            subscription = Subscription.objects.subscribe(feed_url, hub=hub)
        except:
            log.warning("SubscriptionError. Retrying (%s)" % (link.url,))
            self.retry([link, ], kwargs)

        log.debug("Success. Subscribed to topic %s on hub %s" % (
            feed_url, hub))
        link.subscription = subscription
        link.save()


class UnsubscribeFromFeed(Task):
    """Simply send an unsubscribe request to the provided links hub."""

    def run(self, link, **kwargs):
        Subscription.objects.unsubscribe(link.subscription.topic,
                                         hub=link.subscription.hub)


class HandleNotification(Task):
    """
    When a notification of a new or updated entry is received, parse
    the entry and create an activity representation of it.
    """

    def run(self, notification, sender, **kwargs):
        log = self.get_logger(**kwargs)

        for entry in notification.entries:
            log.debug("Received notification of entry: %s, %s" % (
                entry.title, entry.link))
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
