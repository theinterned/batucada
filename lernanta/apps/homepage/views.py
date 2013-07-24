import random

from django.shortcuts import render_to_response
from django.template import RequestContext


from learn.models import get_courses_by_list

from processors import get_schools
from processors import get_feed


def home(request):
    feed_entries = get_feed()
    courses = get_courses_by_list("showcase")
    featured_count = min(4,len(courses))
    courses = random.sample(courses, featured_count)
    schools = get_schools()

    return render_to_response('homepage/home.html', {
        'feed_entries':  feed_entries,
        'courses': courses,
        'schools': schools,
    }, context_instance=RequestContext(request))
