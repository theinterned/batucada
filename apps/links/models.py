import urllib2
import logging

from django.db import models
from django.db.models.signals import post_save

from links import utils

log = logging.getLogger(__name__)


class Link(models.Model):
    name = models.CharField(max_length=100)
    url = models.URLField(max_length=1023)
    project = models.ForeignKey('projects.Project', null=True)
    user = models.ForeignKey('users.UserProfile', null=True)


def link_create_handler(sender, **kwargs):
    link = kwargs.get('instance', None)
    created = kwargs.get('created', False)

    if not created or not isinstance(link, Link):
        return

    try:
        log.debug("Fetching URL (%s)" % (link.url,))
        html = urllib2.urlopen(link.url).read()
        log.debug("Attempting to get feed url")
        feed_url = utils.parse_feed_url(html)
        log.debug("Found feed URL (%s) for link (%s)" % (
            feed_url, link.url))
        feed = urllib2.urlopen(feed_url).read()
        hub_url = utils.parse_hub_url(feed)
        log.debug("Found hub URL (%s) for link (%s)" % (
            hub_url, link.url))
        if hub_url:
            pass  # set up pubsubhubbub subscription
    except:
        log.error("Error getting hub URL for %s" % (link.url,))

post_save.connect(link_create_handler, sender=Link)
