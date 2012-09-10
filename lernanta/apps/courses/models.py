import simplejson as json

from courses import db
from drumbeat.utils import slugify
from django.utils.translation import ugettext as _

import logging
log = logging.getLogger(__name__)

def course_uri2id(course_uri):
    return course_uri.strip('/').split('/')[-1]


def _get_course_db(course_uri):
    course_id = course_uri2id(course_uri)
    try:
        return db.Course.objects.get(id=course_id)
    except:
        return None


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
        "uri": "/uri/course/{0}".format(course_db.id),
        "title": course_db.title,
        "short_title": course_db.short_title,
        "about_uri": "/uri/content/1/",
        "slug": slugify(course_db.title),
        "plug": course_db.plug,
        "creator": "/uri/user/dirk",
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
        # TODO
        return None

    about = create_content({"title": _("About"), "content": ""})
    add_course_content("/uri/course/{0}".format(course_db.id), about['uri'])
    create_course_cohort("/uri/course/{0}".format(course_db.id), "/uri/user/dirk")
    course = get_course("/uri/course/{0}".format(course_db.id))
    return course


def update_course(course_json):
    # TODO
    return False


def get_course_content(course_uri):
    content = []
    course_id = course_uri2id(course_uri)
    course_db = None
    try:
        course_db = db.Course.objects.get(id=course_id)
    except:
        # TODO
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
        # TODO
        pass
    course_content_db = db.CourseContent(
        course=course_db,
        content_uri=content_uri,
        index=next_index
    )
    course_content_db.save()


def update_course_content():
    # TODO
    pass


def delete_course_content():
    # TODO
    pass


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
                "author": "/uri/user/bob/",
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


def create_course_cohort(course_uri, admin_user_uri):
    course_db = _get_course_db(course_uri)
    if not course_db:
        return None

    if course_db.cohort_set.count() != 0:
        return None

    cohort_db = db.Cohort(
        course=course_db,
        term=db.Cohort.ROLLING,
        signup=db.Cohort.OPEN
    )
    cohort_db.save()
    cohort = get_course_cohort(course_uri)
    if not cohort:
        log.error("Could not create new cohort!")
        return None
    add_user_to_cohort(cohort["uri"], admin_user_uri, db.CohortSignup.ORGANIZER)
    return get_course_cohort(course_uri)


def get_course_cohort(course_uri):
    course_db = _get_course_db(course_uri)
    if not course_db:
        return None
    if course_db.cohort_set.count() != 1:
        return None
    return get_cohort(
        "/uri/cohort/{0}".format(course_db.cohort_set.all()[0].id))


def _get_cohort_db(cohort_uri):
    cohort_id = cohort_uri.strip('/').split('/')[-1]
    try:
        return db.Cohort.objects.get(id=cohort_id)
    except:
        return None


def get_cohort(cohort_uri):
    cohort_db = _get_cohort_db(cohort_uri)
    if not cohort_db:
        return None
    cohort_data = {
        "uri": "/uri/cohort/{0}".format(cohort_db.id),
        "course_uri": "/uri/course/{0}".format(cohort_db.course.id),
        "term": cohort_db.term,
        "signup": cohort_db.signup,
    }
    #NOTE: fetching course + cohort twice when using get_course_cohort
    #NOTE-Q: does cohort.course.id fetch the course data?

    if cohort_db.term != db.Cohort.ROLLING:
        cohort_data["start_date"] = cohort_db.start_date
        cohort_data["end_date"] = cohort_db.end_date

    users = []
    for singup in cohort_db.signup_set.all():
        users += [{
            "username": "dirk", "uri": "/uri/user/dirk", "role": "ORGANIZER"
        }]
    cohort_data["users"] = users

    return cohort_data


def add_user_to_cohort(cohort_uri, user_uri, role):
    cohort_db = _get_cohort_db(cohort_uri)
    signup_db = db.CohortSignup(
        cohort=cohort_db,
        user_uri=user_uri,
        role=role
    )
    try:
        signup_db.save()
    except:
        return None
    
    signup = {
        "cohort_uri": cohort_uri,
        "user_uri": user_uri,
        "role": role
    }

    return signup
