import time
import urllib2
import logging
import hashlib
import feedparser

from BeautifulSoup import BeautifulSoup

from django.conf import settings

from celery.schedules import crontab
from celery.decorators import periodic_task

from dashboard.models import FeedEntry

log = logging.getLogger(__name__)


def strip_html(data):
    return ''.join(BeautifulSoup(data).findAll(text=True))


def parse_entry(entry):
    log.debug("parsing %s" % (entry,))
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
        return

    data = urllib2.urlopen(feed_url).read()
    feed = feedparser.parse(data)
    entries = feed.entries[0:4]

    counter = 0
    for entry in entries:
        log.debug("parsing feed")
        parsed = parse_entry(entry)
        if not parsed:
            log.warn("Parsing feed failed. continuing")
            continue
        body = getattr(parsed['content'], 'value', None)
        if not body:
            continue
        cleaned_body = strip_html(body).encode('utf-8')
        try:
            checksum = hashlib.md5(cleaned_body).hexdigest()
            FeedEntry(
                title=parsed['title'].encode('utf-8'),
                link=parsed['link'].encode('utf-8'),
                body=cleaned_body,
                checksum=checksum,
                created_on=time.strftime(
                    "%Y-%m-%d %H:%M:%S", parsed['updated'])).save()
            counter += 1
        except:
            continue

    stale = FeedEntry.objects.all().order_by('-created_on')[:counter]
    for entry in stale:
        entry.delete()
