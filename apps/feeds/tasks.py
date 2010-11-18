import logging
import feedparser

from celery.task.schedules import crontab
from celery.decorators import periodic_task

from projects.models import Link


log = logging.getLogger(__name__)


@periodic_task(run_every=crontab())
def load_project_feeds():
    links = Link.objects.all()
    for link in links:
        feed = feedparser.parse(link.url)
        log.debug(len(feed.entries))
    log.info("Running test task")
