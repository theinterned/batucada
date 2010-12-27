import urllib2

from django.conf import settings

from celery.task import Task
from django_push.subscriber.models import Subscription

from links import utils

import activity


class SubscribeToFeed(Task):

    def run(self, link, **kwargs):
        log = self.get_logger(**kwargs)
        log.debug("Subscribing to feed (%s)" % (link.url,))

        hub_url = None
        try:
            html = urllib2.urlopen(link.url).read()
            feed_url = utils.parse_feed_url(html)
            feed = urllib2.urlopen(feed_url).read()
            hub_url = utils.parse_hub_url(feed)
        except:
            log.debug("Retrying (%s)" % (link.url,))
            self.retry([link, ], kwargs)

        try:
            if hub_url:
                log.debug("Subscribing with hub_url (%s)" % (hub_url,))
                subscription = Subscription.objects.subscribe(feed_url,
                                                          hub=hub_url)
            else:
                log.debug("Subscribing with hub_url (%s)" % (
                    settings.PUSH_DEFAULT_HUB_URL,))
                subscription = Subscription.objects.subscribe(
                    feed_url,
                    hub=settings.PUSH_DEFAULT_HUB_URL)
        except:
            log.debug("SubscriptionError. Retrying (%s)" % (link.url,))
            self.retry([link, ], kwargs)

        link.subscription = subscription
        link.save()


class UnsubscribeFromFeed(Task):

    def run(self, link, **kwargs):
        Subscription.objects.unsubscribe(link.subscription.topic,
                                         hub=link.subscription.hub)


class HandleNotification(Task):

    def run(self, notification, sender, **kwargs):
        log = self.get_logger(**kwargs)
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
        log.debug("Entry content: %s" % (content,))
