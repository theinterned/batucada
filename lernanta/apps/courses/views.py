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
from courses.forms import CourseTitleForm
from courses.forms import CourseTermForm
from courses.forms import CourseLanguageForm
from courses.forms import CourseImageForm

from content2 import models as content_model
from content2.forms import ContentForm

from media import models as media_model

from replies import models as comment_model

log = logging.getLogger(__name__)

@login_required
def create_course( request ):
    if request.method == "POST":
        form = CourseCreationForm(request.POST)
        if form.is_valid():
            user = request.user.get_profile()
            user_uri = "/uri/user/{0}".format(user.username)
            course = {
                'title': form.cleaned_data.get('title'),
                'short_title': form.cleaned_data.get('short_title'),
                'plug': form.cleaned_data.get('plug'),
                'language': form.cleaned_data.get('language'),
                'organizer_uri': user_uri
            }
            course = course_model.create_course(**course)
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
    context['course_url'] = request.get_full_path()

    if 'image_uri' in course:
        context['course']['image'] = media_model.get_image(course['image_uri'])

    cohort = course_model.get_course_cohort(course_uri)
    context['cohort'] = cohort
    user_uri = "/uri/user/{0}".format(request.user.username)
    context['organizer'] = course_model.is_cohort_organizer(
        user_uri, cohort['uri']
    )
    if context['organizer']:
        context['title_form'] = CourseTitleForm(course)
        context['language_form'] = CourseLanguageForm(course)
        context['image_form'] = CourseImageForm()
        if cohort['term'] == 'FIXED':
            context['term_form'] = CourseTermForm(cohort)
        else:
            context['term_form'] = CourseTermForm()
    context['about'] = content_model.get_content(course['about_uri'])
    context['about']['content'] = markdown.markdown(
        context['about']['content'], ['tables']
    )
    context['comments'] = course_model.get_cohort_comments(
        cohort['uri'], course['about_uri']
    )
    if course_model.user_in_cohort(user_uri, cohort['uri']):
        context['show_leave_course'] = True
    elif cohort['signup'] == "OPEN" and course['draft'] == False:
        context['show_signup'] = True
    return render_to_response(
        'courses/course.html',
        context,
        context_instance=RequestContext(request)
    )


@login_required
@require_http_methods(['POST'])
def course_image( request, course_id ):
    course_uri = course_model.course_id2uri(course_id)
    user_uri = "/uri/user/{0}".format(request.user.username)
    #TODO check organizer
    image_form = CourseImageForm(request.POST, request.FILES)
    if image_form.is_valid():
        image_file = request.FILES['image']
        image = media_model.upload_image(image_file, course_uri)
        course_model.update_course(
            course_uri=course_uri,
            image_uri=image['uri'],
        )
    else:
        messages.error(request, _("Could not upload image"))
    return course_slug_redirect( request, course_id )


@login_required
def course_signup( request, course_id ):
    #NOTE: consider using cohort_id in URL to avoid cohort lookup
    cohort = course_model.get_course_cohort( course_id )
    user_uri = "/uri/user/{0}".format(request.user.username)
    course_model.add_user_to_cohort(cohort['uri'], user_uri, "LEARNER")
    return course_slug_redirect( request, course_id )


@login_required
@require_http_methods(['POST'])
def course_add_user( request, course_id ):
    cohort = course_model.get_course_cohort( course_id )
    admin_uri = "/uri/user/{0}".format(request.user.username)
    is_organizer = course_model.is_cohort_organizer(
        admin_uri, cohort['uri']
    )
    username = request.POST.get('username', None)
    if not is_organizer:
        messages.error(request, _("Only organizer are allowed to add new users"))
        return course_slug_redirect(request, course_id)
    if not username:
        messages.error(request, _("Please select a user"))
        return course_slug_redirect(request, course_id)
    user_uri = "/uri/user/{0}".format(username)
    course_model.add_user_to_cohort(cohort['uri'], user_uri, "LEARNER")
    return course_slug_redirect(request, course_id)


@login_required
def course_leave( request, course_id, username ):
    cohort = course_model.get_course_cohort( course_id )
    user_uri = "/uri/user/{0}".format(request.user.username)
    is_organizer = course_model.is_cohort_organizer(
        user_uri, cohort['uri']
    )
    removed = False
    error_message = _("Could not remove user")
    if username == request.user.username or is_organizer:
        removed, error_message = course_model.remove_user_from_cohort(
            cohort['uri'], "/uri/user/{0}".format(username)
        )

    if not removed:
        messages.error(request, error_message)

    return course_slug_redirect( request, course_id)


@login_required
@require_http_methods(['POST'])
def course_add_organizer( request, course_id, username ):
    cohort = course_model.get_course_cohort( course_id )
    user_uri = "/uri/user/{0}".format(request.user.username)
    is_organizer = course_model.is_cohort_organizer(
        user_uri, cohort['uri']
    )
    if not is_organizer:
        messages.error( request, _("Only other organizers can add a new organizer") )
        return course_slug_redirect( request, course_id)
    new_organizer_uri = "/uri/user/{0}".format(username)
    course_model.remove_user_from_cohort(cohort['uri'], new_organizer_uri)
    course_model.add_user_to_cohort(cohort['uri'], new_organizer_uri, "ORGANIZER")

    #TODO
    return course_slug_redirect( request, course_id)


@login_required
@require_http_methods(['POST'])
def course_change_status( request, course_id, status ):
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
@require_http_methods(['POST'])
def course_change_signup( request, course_id, signup ):
    # TODO check organizer
    cohort = course_model.get_course_cohort( course_id )
    cohort['signup'] = signup.upper()
    cohort = course_model.update_cohort(cohort)
    if not cohort:
        messages.error( request, _("Could not change cohort signup"))
    return course_slug_redirect( request, course_id )


@login_required
@require_http_methods(['POST'])
def course_change_term( request, course_id, term ):
    cohort = course_model.get_course_cohort( course_id )
    cohort['term'] = term.upper()
    if term == 'fixed':
        form = CourseTermForm(request.POST)
        if form.is_valid():
            cohort['start_date'] = form.cleaned_data['start_date']
            cohort['end_date'] = form.cleaned_data['end_date']
            cohort = course_model.update_cohort(cohort)
        else:
            messages.error( request, _("Could not update fixed term dates"))
    elif term == 'rolling':
        cohort = course_model.update_cohort(cohort)
    return course_slug_redirect( request, course_id)


@login_required
@require_http_methods(['POST'])
def course_update_title( request, course_id ):
    # TODO check organizer
    course_uri = course_model.course_id2uri(course_id)
    form = CourseTitleForm(request.POST)
    if form.is_valid():
        course_model.update_course(
            course_uri,
            title=form.cleaned_data['title']
        )
    else:
        messages.error(request, _("Could not update course title"))
    return course_slug_redirect( request, course_id )


@login_required
@require_http_methods(['POST'])
def course_change_language( request, course_id ):
    # TODO check organizer
    course_uri = course_model.course_id2uri(course_id)
    form = CourseLanguageForm(request.POST)
    if form.is_valid():
        course_model.update_course(
            course_uri,
            language=form.cleaned_data['language']
        )
    return course_slug_redirect( request, course_id )


def show_content( request, course_id, content_id):
    content_uri = '/uri/content/{0}'.format(content_id)
    user_uri = "/uri/user/{0}".format(request.user.username)
    content = content_model.get_content(content_uri)
    content['rows'] = content['content'].count('\n')
    course = course_model.get_course('/uri/course/{0}/'.format(course_id))
    cohort = course_model.get_course_cohort('/uri/course/{0}/'.format(course_id))
    context = { 
        'content': content, 
        'course': course,
    }
    context['comments'] = course_model.get_cohort_comments(cohort['uri'], content['uri'])
    context['organizer'] = course_model.is_cohort_organizer(
        user_uri, cohort['uri']
    )
    context['can_edit'] = context['organizer']
    context['form'] = ContentForm(content)
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

            redirect_url = request.POST.get('next_url', None)
            if not redirect_url:
                redirect_url = reverse('courses_show',
                    kwargs={'course_id': course['id'], 'slug': course['slug']}
                )
            return http.HttpResponseRedirect(redirect_url)
    else:
        form = ContentForm()

    context = { 'form': form }
    if request.GET.get('next_url', None):
        context['next_url'] = request.GET.get('next_url', None)

    return render_to_response('courses/create_content.html', 
        context, context_instance=RequestContext(request)
    )


@login_required
def edit_content( request, course_id, content_id ):
    content = content_model.get_content("/uri/content/{0}".format(content_id))

    #TODO Check users permission

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
            
            redirect_url = request.POST.get('next_url', None)
            if not redirect_url:
                redirect_url = reverse('courses_content_show',
                    kwargs={'course_id': course_id, 'content_id': content_id}
                )
            return http.HttpResponseRedirect(redirect_url)
    else:
        form = ContentForm(content)

    context = { 'form': form }
    if request.GET.get('next_url', None):
        context['next_url'] = request.GET.get('next_url', None)
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

    if request.POST.get('next_url'):
        redirect_url = request.POST.get('next_url')
    else:
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

    if request.POST.get('next_url'):
        redirect_url = request.POST.get('next_url')
    else:
        redirect_url = reverse('courses_content_show',
            kwargs={'course_id': course_id, 'content_id': content_id}
        )
    return http.HttpResponseRedirect(redirect_url)
