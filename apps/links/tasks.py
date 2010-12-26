import urllib2

from django.conf import settings

from celery.task import Task
from django_push.subscriber.models import Subscription

from links import utils


class SubscribeToFeed(Task):

    def run(self, link, **kwargs):
        log = self.get_logger(**kwargs)
        log.info("Subscribing to feed (%s)" % (link.url,))

        hub_url = None
        try:
            html = urllib2.urlopen(link.url).read()
            feed_url = utils.parse_feed_url(html)
            feed = urllib2.urlopen(feed_url).read()
            hub_url = utils.parse_hub_url(feed)
        except:
            self.retry([link, ], kwargs)

        try:
            if hub_url:
                subscription = Subscription.objects.subscribe(feed_url,
                                                          hub=hub_url)
            else:
                subscription = Subscription.objects.subscribe(
                    feed_url,
                    hub=settings.SUPERFEEDR_HUB_URL)
        except:
            self.retry([link, ], kwargs)

        link.subscription = subscription
        link.save()


class UnsubscribeFromFeed(Task):

    def run(self, link, **kwargs):
        Subscription.objects.unsubscribe(link.subscription.topic,
                                         hub=link.subscription.hub)
