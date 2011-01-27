import time
import urllib2
import logging
import hashlib
import feedparser
import bleach

from django.conf import settings
from django.utils.encoding import smart_str

from celery.schedules import crontab
from celery.decorators import periodic_task

from dashboard.models import FeedEntry

log = logging.getLogger(__name__)


def parse_entry(entry):
    title = getattr(entry, 'title', None)
    content = getattr(entry, 'content', None)
    link = getattr(entry, 'link', None)
    updated = getattr(entry, 'updated_parsed', None)
    if not (title and content and link and updated):
        log.debug("No title or no content or no link or no updated")
        return None
    if type(content) == type([]):
        content = content[0]
    return {
        'title': title,
        'content': content,
        'link': link,
        'updated': updated,
    }


@periodic_task(run_every=crontab(minute=0, hour=0))
def update_feeds():
    feed_url = getattr(settings, 'SPLASH_PAGE_FEED', None)
    log.debug("update_feeds called with feed url %s" % (feed_url,))

    if not feed_url:
        log.warn("No feed url defined. Cannot update splash page feed.")
        return

    data = urllib2.urlopen(feed_url).read()
    feed = feedparser.parse(data)
    entries = feed.entries[0:4]

    ids = []
    for entry in entries:
        parsed = parse_entry(entry)
        if not parsed:
            log.warn("Parsing feed failed. continuing")
            continue
        body = getattr(parsed['content'], 'value', None)
        if not body:
            log.warn("Parsing feed failed - no body found")
            continue
        cleaned_body = smart_str(bleach.clean(body, tags=(), strip=True))
        try:
            checksum = hashlib.md5(cleaned_body).hexdigest()
            exists = FeedEntry.objects.filter(checksum=checksum)
            if not exists:
                entry = FeedEntry(
                    title=parsed['title'].encode('utf-8'),
                    link=parsed['link'].encode('utf-8'),
                    body=cleaned_body,
                    checksum=checksum,
                    created_on=time.strftime(
                        "%Y-%m-%d %H:%M:%S", parsed['updated']))
                entry.save()
                ids.append(entry.id)
        except:
            log.warn("Encountered an error creating FeedEntry. Skipping.")
            continue

    FeedEntry.objects.exclude(id__in=ids).delete()
