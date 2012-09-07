import logging

from django import http
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _

from l10n.urlresolvers import reverse
from users.models import UserProfile
from users.decorators import login_required

from courses import models as course_model
from courses.forms import CourseCreationForm

log = logging.getLogger(__name__)

def create_course( request ):
    if request.method == "POST":
        form = CourseCreationForm(request.POST)
        if form.is_valid():
            course = {
                'title': form.cleaned_data.get('title'),
                'short_title': form.cleaned_data.get('short_title'),
                'plug': form.cleaned_data.get('plug'),
            }
            course = course_model.create_course(course)
            redirect_url = reverse('courses_show', 
                kwargs={'course_id': course['id'], 'slug': course['slug']}
            )
            return http.HttpResponseRedirect(redirect_url)
    else:
        form = CourseCreationForm()

    context = { 'form': form }
    return render_to_response('courses/create_course.html', 
        context, context_instance=RequestContext(request)
    )


def course_slug_redirect( request, course_id ):
    course = course_model.get_course('/uri/courses/{0}/'.format(course_id))
    if course == None:
        raise http.Http404

    redirect_url = reverse('courses_show', 
        kwargs={'course_id': course_id, 'slug': course['slug']})
    return http.HttpResponseRedirect(redirect_url)


def show_course( request, course_id, slug=None ):
    course = course_model.get_course('/uri/courses/{0}/'.format(course_id))
    if course == None:
        raise http.Http404
 
    if slug != course['slug']:
        return course_slug_redirect( request, course_id)

    context = { 'course': course }
    context['about'] = course_model.get_content(course['about_uri'])
    context['cohort'] = course_model.get_course_cohort(course)
    return render_to_response('courses/course.html', context, context_instance=RequestContext(request))


def show_content( request, course_id, content_id):

    content = course_model.get_content('/uri/content/{0}'.format(content_id))
    course = course_model.get_course('/uri/courses/{0}/'.format(course_id))
    context = { 'content': content }
    context['course_id'] = course_id
    context['course_slug'] = course['slug']
    context['course_title'] = course['title']
    return render_to_response('courses/content.html', context, context_instance=RequestContext(request))

