from schools.models import School
from news.models import FeedEntry

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
