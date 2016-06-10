import urllib2

from django.conf import settings

from celery.task import Task
from django_push.subscriber.models import Subscription, SubscriptionError

from links import utils
from activity.models import RemoteObject, Activity
from activity.schema import verbs, object_types


class SubscribeToFeed(Task):
    """
    Try to discover an Atom or RSS feed for the provided link and
    subscribe to it. Try to discover a hub declaration for the feed.
    If no hub is declared, fall back to using SuperFeedr.
    """
    name = 'links.tasks.SubscribeToFeed'

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
            log.warning("Error discovering feed URL for %s. Retrying." % (
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
            log.warning("Error discovering hub URL for %s. Retrying." % (
                feed_url,))
            self.retry([link, ], kwargs)

        try:
            hub = hub_url or settings.SUPERFEEDR_URL
            log.debug("Attempting subscription of topic %s with hub %s" % (
                feed_url, hub))
            subscription = Subscription.objects.subscribe(feed_url, hub=hub)
            log.info("Created subscription with callback url: %s" % (
                subscription.callback_url,))
        except SubscriptionError, e:
            log.warning("SubscriptionError. Retrying (%s)" % (link.url,))
            log.warning("Error: %s" % (str(e),))
            self.retry([link, ], kwargs)

        log.debug("Success. Subscribed to topic %s on hub %s" % (
            feed_url, hub))
        link.subscription = subscription
        link.save()


class UnsubscribeFromFeed(Task):
    """Simply send an unsubscribe request to the provided links hub."""
    name = 'links.tasks.UnsubscribeFromFeed'

    def run(self, link, **kwargs):
        Subscription.objects.unsubscribe(link.subscription.topic,
                                         hub=link.subscription.hub)


class HandleNotification(Task):
    """
    When a notification of a new or updated entry is received, parse
    the entry and create an activity representation of it.
    """
    name = 'links.tasks.HandleNotification'

    def get_activity_namespace_prefix(self, feed):
        """Discover the prefix used for the activity namespace."""
        namespaces = feed.namespaces
        activity_prefix = [prefix for prefix, ns in namespaces.iteritems()
                           if ns == 'http://activitystrea.ms/spec/1.0/']
        if activity_prefix:
            return activity_prefix[0]
        return None

    def get_namespaced_attr(self, entry, prefix, attr):
        """Feedparser prepends namespace prefixes to attribute names."""
        qname = '_'.join((prefix, attr))
        return getattr(entry, qname, None)

    def create_activity_entry(self, entry, sender, activity_prefix=None):
        """Create activity feed entries for the provided feed entry."""
        object_type = None
        if activity_prefix:
            object_type = self.get_namespaced_attr(
                entry, activity_prefix, 'object-type')
        if not object_type:
            object_type = object_types['article']
        title = getattr(entry, 'title', None)
        uri = getattr(entry, 'link', None)
        if not title:
            title = entry.get('title')
        if not uri:
            uris = entry.get('links')
            if uris:
                uri = uris[0].get('href')
        if not (title and uri):
            return
        for link in sender.link_set.all():
            remote_obj = RemoteObject(
                link=link, title=title, uri=uri, object_type=object_type)
            remote_obj.save()
            activity = Activity(
                actor=link.user, verb=verbs['share'], target_object=remote_obj)
            if link.project:
                activity.scope_object = link.project
            activity.save()

    def run(self, notification, sender, **kwargs):
        """Parse feed and create activity entries."""
        prefix = self.get_activity_namespace_prefix(notification)
        for entry in notification.entries:
            self.create_activity_entry(entry, sender, activity_prefix=prefix)
