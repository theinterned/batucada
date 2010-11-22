import logging
import hashlib
import datetime

import feedparser
import activity

from celery.task.schedules import crontab
from celery.decorators import periodic_task

from feeds.models import Entry, RemoteObject
from projects.models import Link

log = logging.getLogger(__name__)


def _process_feed_entry(link, entry):
    """Process a single feed entry, creating activity if not already seen."""
    signature = hashlib.md5(str(entry)).hexdigest()
    log.debug("Calculated feed entry signature: %s" % (signature,))
    try:
        Entry.objects.get(signature__exact=signature)
        log.debug("Already encountered: %s, skipping" % (signature,))
        return
    except Entry.DoesNotExist:
        pass
    Entry(link=link, signature=signature).save()
    d = datetime.datetime(*entry.updated_parsed[0:6])
    obj = RemoteObject(title=entry.title, url=entry.link)
    obj.save()
    activity.send(entry.author, 'post', obj, link.project, d)


@periodic_task(run_every=crontab())
def load_project_feeds():
    links = Link.objects.all()
    for link in links:
        feed = feedparser.parse(link.feed_url)
        for entry in feed.entries:
            _process_feed_entry(link, entry)
