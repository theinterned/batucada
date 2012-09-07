import simplejson as json

from courses import db
from drumbeat.utils import slugify
from django.utils.translation import ugettext as _

import logging
log = logging.getLogger(__name__)

def course_uri2id(course_uri):
    return course_uri.strip('/').split('/')[-1]


def get_course(course_uri):
    course_id = course_uri2id(course_uri)
    course_db = None
    try:
        course_db = db.Course.objects.get(id=course_id)
    except:
        #TODO
        return None

    course = {
        "id": 1,
        "title": course_db.title,
        "short_title": course_db.short_title,
        "about_uri": "/uri/content/1/",
        "slug": slugify(course_db.title),
        "plug": course_db.plug,
        "creator": "/users/dirk",
        "content": get_course_content(course_uri),
    }
    return course


def create_course(course_data):
    course_db = db.Course(
        title=course_data['title'],
        short_title=course_data['short_title'],
        plug=course_data['plug']
    )

    course_db.save()
    try:
        course_db.save()
    except:
        #TODO
        return None

    about = create_content({"title": _("About"), "content": ""})
    add_course_content("/uri/course/{0}".format(course_db.id), about['uri'])
    course = get_course("/uri/course/{0}".format(course_db.id))
    return course


def update_course(course_json):
    return False


def get_course_content(course_uri):
    content = []
    course_id = course_uri2id(course_uri)
    course_db = None
    try:
        course_db = db.Course.objects.get(id=course_id)
    except:
        #TODO
        return None
    for course_content_db in course_db.content.order_by('index'):
        content_data = get_content(course_content_db.content_uri)
        content += [{
            "id": content_data["id"],
            "uri": content_data["uri"],
            "title": content_data["title"],
            "index": course_content_db.index,
        }]

    return content


def add_course_content(course_uri, content_uri):
    course_id = course_uri2id(course_uri)
    course_db = None
    try:
        course_db = db.Course.objects.get(id=course_id)
    except:
        return None
    next_index = 0
    try:
        next_index = db.CourseContent.objects.filter(course = course_db).order_by('index')[0].index
    except:
        #TODO
        pass
    course_content_db = db.CourseContent(
        course=course_db,
        content_uri=content_uri,
        index=next_index
    )
    course_content_db.save()


def content_uri2id(content_uri):
    return content_uri.strip('/').split('/')[-1]

#TODO seperate from course stuff
def get_content(content_uri, fields=[]):
    content_id = content_uri2id(content_uri)
    try:
        wrapper_db = db.Content.objects.get(id=content_id)
        latest_db = wrapper_db.latest
    except Exception, e:
        #TODO
        log.debug(e)
        return None
    
    content = {
        "id": wrapper_db.id,
        "uri": "/uri/content/{0}".format(wrapper_db.id),
        "title": latest_db.title,
        "content": latest_db.content,
    }
    if "history" in fields:
        content["history"] = []
        for version in wrapper_db.versions.sort_by("date"):
            content['history'] += {
                "date": version.date,
                "author": "/users/bob/",
                "title": version.title,
                "comment": version.comment,
            }

    return content


#TODO seperate from course stuff
def create_content(content):
    #TODO check all required properties
    container_db = db.Content()
    container_db.save()
    content_db = db.ContentVersion(
        container=container_db,
        title=content["title"],
        content=content["content"],
    )
    if "comment" in content:
        content_db.comment = content["comment"]
    content_db.save()
    container_db.latest = content_db
    container_db.save()
    return get_content("/uri/content/{0}".format(container_db.id))


def get_course_cohort(course_uri):
    cohort_json = """{
        "course": "/courses/1",
        "term": "ROLLING",
        "signup": "OPEN",
        "users": [
            {"username": "dirk", "uri": "/users/dirk", "role": "organizer"},
            {"username": "bob", "uri": "/users/bob", "role": "learner"}
        ]
    }"""
    return json.loads(cohort_json)


def add_user_to_cohort(cohort_uri, user_uri, role):
    pass
