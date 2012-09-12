import logging

from django import http
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _

from l10n.urlresolvers import reverse
from users.models import UserProfile
from users.decorators import login_required
from drumbeat import messages

from courses import models as course_model
from courses.forms import CourseCreationForm

from content2 import models as content_model
from content2.forms import ContentForm

log = logging.getLogger(__name__)

@login_required
def create_course( request ):
    if request.method == "POST":
        form = CourseCreationForm(request.POST)
        if form.is_valid():
            course = {
                'title': form.cleaned_data.get('title'),
                'short_title': form.cleaned_data.get('short_title'),
                'plug': form.cleaned_data.get('plug'),
            }
            user = request.user.get_profile()
            user_uri = "/uri/user/{0}".format(user.username)
            course = course_model.create_course(course, user_uri)
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
    course = course_model.get_course('/uri/course/{0}/'.format(course_id))
    if course == None:
        raise http.Http404

    redirect_url = reverse('courses_show', 
        kwargs={'course_id': course_id, 'slug': course['slug']})
    return http.HttpResponseRedirect(redirect_url)


def show_course( request, course_id, slug=None ):
    course_uri = '/uri/course/{0}/'.format(course_id)
    course = course_model.get_course(course_uri)
    if course == None:
        raise http.Http404
 
    if slug != course['slug']:
        return course_slug_redirect( request, course_id)

    context = { 'course': course }
    context['about'] = content_model.get_content(course['about_uri'])
    context['cohort'] = course_model.get_course_cohort(course_uri)
    context['organizer'] = True #TODO
    
    user = request.user.get_profile()
    user_uri = "/uri/user/{0}".format(user.username)
    if not course_model.user_in_cohort(user_uri, context['cohort']['uri']):
        context['show_signup'] = True
    return render_to_response('courses/course.html', context, context_instance=RequestContext(request))


@login_required
def course_signup( request, course_id ):
    #NOTE: consider using cohort_id in URL to avoid cohort lookup
    cohort = course_model.get_course_cohort( course_id )
    user = request.user.get_profile()
    user_uri = "/uri/user/{0}".format(user.username)
    course_model.add_user_to_cohort(cohort['uri'], user_uri, "LEARNER")
    return course_slug_redirect( request, course_id )


@login_required
def course_leave( request, course_id, username ):
    cohort = course_model.get_course_cohort( course_id )
    user = request.user.get_profile()
    user_uri = "/uri/user/{0}".format(user.username)
    # check if user is in admin or trying to remove himself
    removed = False
    error_message = _("Could not remove user")
    if username == user.username:
        removed, error_message = course_model.remove_user_from_cohort(cohort['uri'], user_uri)

    if not removed:
        messages.error(request, error_message)

    return course_slug_redirect( request, course_id)


def show_content( request, course_id, content_id):
    content = content_model.get_content('/uri/content/{0}'.format(content_id))
    course = course_model.get_course('/uri/course/{0}/'.format(course_id))
    context = { 'content': content }
    context['course_id'] = course_id
    context['course_slug'] = course['slug']
    context['course_title'] = course['title']
    return render_to_response('courses/content.html', context, context_instance=RequestContext(request))


@login_required
def create_content( request, course_id ):
    course = course_model.get_course('/uri/course/{0}/'.format(course_id))
    if request.method == "POST":
        form = ContentForm(request.POST)
        if form.is_valid():
            content_data = {
                'title': form.cleaned_data.get('title'),
                'content': form.cleaned_data.get('content'),
            }
            user = request.user.get_profile()
            user_uri = "/uri/user/{0}".format(user.username)
            content = content_model.create_content(content_data, user_uri)
            course_model.add_course_content(course['uri'], content['uri'])
            redirect_url = reverse('courses_show',
                kwargs={'course_id': course['id'], 'slug': course['slug']}
            )
            return http.HttpResponseRedirect(redirect_url)
    else:
        form = ContentForm()

    context = { 'form': form }
    return render_to_response('courses/create_content.html', 
        context, context_instance=RequestContext(request)
    )


@login_required
def edit_content( request, course_id, content_id ):
    content = content_model.get_content("/uri/content/{0}".format(content_id))

    if request.method == "POST":
        form = ContentForm(request.POST)
        if form.is_valid():
            content_data = {
                'title': form.cleaned_data.get('title'),
                'content': form.cleaned_data.get('content'),
            }
            user = request.user.get_profile()
            user_uri = "/uri/user/{0}".format(user.username)
            content = content_model.update_content(
                content['uri'], content_data, user_uri
            )
            return course_slug_redirect( request, course_id )
    else:
        form = ContentForm(content)

    context = { 'form': form }
    return render_to_response('courses/edit_content.html', 
        context, context_instance=RequestContext(request)
    )

