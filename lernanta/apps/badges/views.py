import logging

from django import http
from django.utils.translation import ugettext as _
from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.template import RequestContext
from django.template.loader import render_to_string

from django_obi.views import send_badges

from users.decorators import login_required
from drumbeat import messages
from l10n.urlresolvers import reverse

from badges import forms as badge_forms
from badges.pilot import get_badge_url
from badges.models import Badge, Submission, Rubric, Assessment


log = logging.getLogger(__name__)


def badge_description(request, slug):
    pilot_url = get_badge_url(slug)
    if pilot_url:
        return http.HttpResponseRedirect(pilot_url)
    else:
        raise http.Http404


def show(request, slug):
    badge = get_object_or_404(Badge, slug=slug)
    user = request.user
    is_eligible = False
    rubrics = get_list_or_404(Rubric, badges=badge)
    if user is not None:
        is_eligible = badge.is_eligible(user)
        #TODO application_pending =
    context = {
        'badge': badge,
        'is_eligible': is_eligible,
        'rubrics': rubrics,
    }
    return render_to_response('badges/badge.html', context,
        context_instance=RequestContext(request))


@login_required
def create(request):
    if request.method == 'POST':
        form = badge_forms.BadgeForm(request.POST)
        if form.is_valid():
            badge = form.save()
            badge.create()
            messages.success(request,
                _('The %s has been created.') % badge.name)
            return http.HttpResponseRedirect(reverse('badges_show', kwargs={
                'slug': badge.slug,
            }))
        else:
            msg = _("Problem creating the badge.")
            messages.error(request, msg)
    else:
        form = badge_forms.BadgeForm()
    return render_to_response('badges/badge_edit_summary.html', {
        'form': form, 'new_tab': True,
    }, context_instance=RequestContext(request))


@login_required
def badges_manage_complete(request):
    msg = render_to_string('badges/success_msg.html', dict(
        obi_url=settings.MOZBADGES['hub'], email=request.user.email))
    messages.info(request, msg)
    return http.HttpResponseRedirect(reverse('users_badges_manage'))


@login_required
def badges_manage_render_failure(request, message, status=500):
    log.error('Error sending badges to the OBI: %s' % message)
    msg = _("Something has gone wrong. Hopefully it's temporary. ")
    msg += _("Please try again in a few minutes.")
    messages.error(request, msg)
    return http.HttpResponseRedirect(reverse('users_badges_manage'))


@login_required
def badges_manage(request):
    profile = request.user.get_profile()
    badges_help_url = reverse('static_page_show', kwargs=dict(
            slug='assessments-and-badges'))
    return send_badges(request,
        template_name='badges/profile_badges_manage.html',
        send_badges_complete_view='users_badges_manage_done',
        render_failure=badges_manage_render_failure,
        extra_context=dict(profile=profile, obi_url=settings.MOZBADGES['hub'],
        badges_help_url=badges_help_url, badges_tab=True))


@login_required
def create_submission(request, slug):
    badge = get_object_or_404(Badge, slug=slug)

    can_apply = badge.is_eligible(request.user)

    if not can_apply:
        messages.error(request, _('You are lacking one or more of the requirements.'))
        # TODO: Reason why
        return http.HttpResponseRedirect(badge.get_absolute_url())
    user = request.user.get_profile()
    submission = None
    if request.method == 'POST':
        form = badge_forms.SubmissionForm(request.POST)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.badge = badge
            submission.author = user
            if 'show_preview' not in request.POST:
                submission.save()
                messages.success(request, _('Submission created and out for review!'))
                return http.HttpResponseRedirect(badge.get_absolute_url())
        else:
            messages.error(request, _('Please correct errors below.'))
    else:
        form = badge_forms.SubmissionForm(instance=badge)

    context = {
        'form': form,
        'badge': badge
    }
    return render_to_response('badges/submission_edit.html', context,
                              context_instance=RequestContext(request))


def show_submission(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)
    badge = submission.badge
    progress = badge.progress_for(submission.author)
    rubrics = get_list_or_404(Rubric, badges=badge)
    assessments = Assessment.objects.filter(submission=submission_id)
    context = {
        'badge': badge,
        'submission': submission,
        'progress': progress,
        'rubrics': rubrics,
        'assessments': assessments, 
        }

    return render_to_response('badges/submission_show.html', context,
                              context_instance=RequestContext(request))


def show_assessment(request, assessment_id):
    assessment = get_object_or_404(Assessment, id=assessment_id)
    badge = assessment.badge 

    context = {
        'assessment': assessment,
        'badge': badge,
        }

    return render_to_response('badges/_assessment_body.html', context,
                              context_instance=RequestContext(request))