import time
import urllib2
import hashlib
import feedparser

from BeautifulSoup import BeautifulSoup

from django.conf import settings

from celery.schedules import crontab
from celery.decorators import periodic_task

from dashboard.models import FeedEntry


def strip_html(data):
    return ''.join(BeautifulSoup(data).findAll(text=True))


def parse_entry(entry):
    title = getattr(entry, 'title', None)
    content = getattr(entry, 'content', None)
    link = getattr(entry, 'link', None)
    updated = getattr(entry, 'updated_parsed', None)
    if not (title and content and link and updated):
        return None
    body = getattr(content, 'value', None)
    if not body:
        return None
    return {
        'title': title,
        'content': body,
        'link': link,
        'updated': updated,
    }


@periodic_task(run_every=crontab(minute=0, hour=0))
def update_feeds():
    feed_url = getattr(settings, 'SPLASH_PAGE_FEED', None)

    if not feed_url:
        return

    data = urllib2.urlopen(feed_url).read()
    feed = feedparser.parse(data)
    entries = feed.entries[0:4]

    counter = 0
    for entry in entries:
        parsed = parse_entry(entry)
        if not parsed:
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

    FeedEntry.objects.all()[counter:].delete()
