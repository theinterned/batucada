import simplejson as json

from courses import db
from drumbeat.utils import slugify


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
        "about_uri": "/uri/content/1",
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

    return get_course(course_db.id)


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
    for content_db in course_db.content.order_by('index'):
        content += [{
            "id": content_db.content.id,
            "title": content_db.content.title,
            "uri": "/uri/content/{0}".format(content_db.content.id),
            "index": content_db.index,
        }]

    return content


def add_course_content(course_uri, content_uri):
    pass


def content_uri2id(content_uri):
    return content_uri.strip('/').split('/')[-1]


def get_content(content_uri):
    from content.models import Page, PageVersion

    content_id = content_uri2id(content_uri)
    try:
        page_db = Page.objects.get(id=content_id)
    except:
        #TODO
        return None
    
    content = {
        "id": page_db.id,
        "title": page_db.title,
        "content": page_db.content,
        "history": [
            { 
                "date": "2012-07-07 00:00:00", 
                "author": "/users/bob/", 
                "title": "Title of the page", 
                "comment": "changed title" 
            },
        ]
    }
    return content


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
