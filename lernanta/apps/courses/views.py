import logging
import markdown

from django import http
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_http_methods

from l10n.urlresolvers import reverse
from users.models import UserProfile
from users.decorators import login_required
from drumbeat import messages

from courses import models as course_model
from courses.forms import CourseCreationForm

from content2 import models as content_model
from content2.forms import ContentForm

from replies import models as comment_model

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
    course_uri = course_model.course_id2uri(course_id)
    course = course_model.get_course(course_uri)
    if course == None:
        raise http.Http404

    redirect_url = reverse('courses_show', 
        kwargs={'course_id': course_id, 'slug': course['slug']})
    return http.HttpResponseRedirect(redirect_url)


def show_course( request, course_id, slug=None ):
    course_uri = course_model.course_id2uri(course_id)
    course = course_model.get_course(course_uri)
    if course == None:
        raise http.Http404
 
    if slug != course['slug']:
        return course_slug_redirect( request, course_id)

    context = { 'course': course }
    context['about'] = content_model.get_content(course['about_uri'])
    context['about']['content'] = markdown.markdown(
        context['about']['content'], ['tables']
    )
    cohort = course_model.get_course_cohort(course_uri)
    context['cohort'] = cohort
    context['comments'] = course_model.get_cohort_comments(
        cohort['uri'], course['about_uri']
    )
    
    user_uri = "/uri/user/{0}".format(request.user.username)
    if not course_model.user_in_cohort(user_uri, cohort['uri']):
        context['show_signup'] = True
    context['organizer'] = True #TODO
    return render_to_response(
        'courses/course.html',
        context,
        context_instance=RequestContext(request)
    )


@login_required
def course_signup( request, course_id ):
    #NOTE: consider using cohort_id in URL to avoid cohort lookup
    cohort = course_model.get_course_cohort( course_id )
    user_uri = "/uri/user/{0}".format(request.user.username)
    course_model.add_user_to_cohort(cohort['uri'], user_uri, "LEARNER")
    return course_slug_redirect( request, course_id )


@login_required
def course_leave( request, course_id, username ):
    cohort = course_model.get_course_cohort( course_id )
    user_uri = "/uri/user/{0}".format(request.user.username)
    # check if user is in admin or trying to remove himself
    removed = False
    error_message = _("Could not remove user")
    if username == request.user.username:
        removed, error_message = course_model.remove_user_from_cohort(cohort['uri'], user_uri)

    if not removed:
        messages.error(request, error_message)

    return course_slug_redirect( request, course_id)


@login_required
def course_status( request, course_id, status ):
    # TODO check organizer
    cohort = course_model.get_course_cohort( course_id )
    user_uri = "/uri/user/{0}".format(request.user.username)
    course_uri = course_model.course_id2uri(course_id)
    if status == 'publish':
        course = course_model.publish_course(course_uri)
    elif status == 'archive':
        course = course_model.archive_course(course_uri)
    return course_slug_redirect( request, course_id )


@login_required
def course_change_signup( request, course_id, signup ):
    # TODO check organizer
    cohort = course_model.get_course_cohort( course_id )
    cohort['signup'] = signup.upper()
    cohort = course_model.update_cohort(cohort)
    if not cohort:
        messages.error( request, _("Could not change cohort signup"))
    return course_slug_redirect( request, course_id )

def show_content( request, course_id, content_id):
    content_uri = '/uri/content/{0}'.format(content_id)
    content = content_model.get_content(content_uri)
    course = course_model.get_course('/uri/course/{0}/'.format(course_id))
    cohort = course_model.get_course_cohort('/uri/course/{0}/'.format(course_id))
    context = { 'content': content }
    context['content']['content'] = markdown.markdown(context['content']['content'])
    context['course_id'] = course_id
    context['course_slug'] = course['slug']
    context['course_title'] = course['title']
    context['comments'] = course_model.get_cohort_comments(cohort['uri'], content['uri'])
    return render_to_response(
        'courses/content.html', 
        context, 
        context_instance=RequestContext(request)
    )


@login_required
def create_content( request, course_id ):
    course_uri = course_model.course_id2uri(course_id)
    course = course_model.get_course(course_uri)
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
            redirect_url = reverse('courses_content_show',
                kwargs={'course_id': course_id, 'content_id': content_id}
            )
            return http.HttpResponseRedirect(redirect_url)
    else:
        form = ContentForm(content)

    context = { 'form': form }
    return render_to_response('courses/edit_content.html', 
        context, context_instance=RequestContext(request)
    )


@login_required
def content_up( request, course_id, content_id ):
    #TODO check admin
    result = course_model.reorder_course_content(
        "/uri/content/{0}".format(content_id), "UP"
    )
    if not result:
        messages.error(request, _("Could not move content up!"))
    return course_slug_redirect( request, course_id )


@login_required
def content_down( request, course_id, content_id ):
    #TODO check admin
    result = course_model.reorder_course_content(
        "/uri/content/{0}".format(content_id), "DOWN"
    )
    if not result:
        messages.error(request, _("Could not move content down!"))
    return course_slug_redirect( request, course_id )


@login_required
@require_http_methods(['POST'])
def post_content_comment( request, course_id, content_id):
    #TODO use form with field that sanitizes the input!
    comment_content = request.POST.get('comment')
    user = request.user.get_profile()
    user_uri = "/uri/user/{0}".format(user.username)
    comment = comment_model.create_comment(comment_content, user_uri)

    reference_uri = "/uri/content/{0}".format(content_id)
    course_uri = course_model.course_id2uri(course_id)
    cohort = course_model.get_course_cohort(course_uri)
    course_model.add_comment_to_cohort(
        comment['uri'], cohort['uri'], reference_uri
    )

    redirect_url = reverse('courses_content_show', 
        kwargs={'course_id': course_id, 'content_id': content_id}
    )
    return http.HttpResponseRedirect(redirect_url)


@login_required
@require_http_methods(['POST'])
def post_comment_reply( request, course_id, content_id, comment_id):
    #TODO use form with field that sanitizes the input!
    comment_content = request.POST.get('comment')
    user = request.user.get_profile()
    user_uri = "/uri/user/{0}".format(user.username)
    comment_uri = "/uri/comment/{0}".format(comment_id)
    reply = comment_model.reply_to_comment(
        comment_uri, comment_content, user_uri
    )

    #TODO: need to set reference so that lookup from comment works!

    redirect_url = reverse('courses_content_show',
        kwargs={'course_id': course_id, 'content_id': content_id}
    )
    return http.HttpResponseRedirect(redirect_url)
