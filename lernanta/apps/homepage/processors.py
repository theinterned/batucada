from schools.models import School
from news.models import FeedEntry

from django.core.cache import cache
from django.utils import simplejson as json
from django.conf import settings

import requests

import logging

log = logging.getLogger(__name__)


def _school_2_dict(school):
    school = {
        'name': school.name,
        'description': school.description,
        'groups_icon': school.groups_icon,
    }
    return school


def get_schools():
    schools = School.objects.all().order_by('id')[:5]
    return [_school_2_dict(school) for school in schools]


def get_feed():
    feed_entries = FeedEntry.objects.filter(
        page='splash').order_by('-created_on')
    return feed_entries



def get_featured_badges():
    badges = cache.get('featured_badges')
    if badges is None:
        try:
            badges = requests.get(settings.FEATURED_BADGES_FEED_URL).json
            cache.set('featured_badges', json.dumps(badges), 60*60)
        except Exception:
            log.error('Could not fetch list of featured badges')
    else:
        badges = json.loads(badges)
    return badges

