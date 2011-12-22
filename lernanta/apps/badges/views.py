import logging

from django import http
from django.utils.translation import ugettext as _
from django.conf import settings
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson

from django_obi.views import send_badges

from users.decorators import login_required
from users.models import UserProfile
from drumbeat import messages
from l10n.urlresolvers import reverse
from pagination.views import get_pagination_context

from badges import forms as badge_forms
from badges.pilot import get_badge_url
from badges.models import Badge, Submission, Assessment

from django.utils import simplejson

log = logging.getLogger(__name__)


def pilot_badge_redirect(request, slug):
    pilot_url = get_badge_url(slug)
    if pilot_url:
        return http.HttpResponseRedirect(pilot_url)
    else:
        raise http.Http404


@login_required
def badges_manage(request):
    #FIXME: Re-enable after updating integration with the OBI.
    raise http.Http404
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


def show_badge(request, slug):
    try:
        badge = Badge.objects.get(slug=slug)
    except Badge.DoesNotExist:
        return pilot_badge_redirect(request, slug)
    is_eligible = badge.is_eligible(request.user)
    applications = []
    rubrics = badge.rubrics.all()
    peer_assessment = (badge.assessment_type == Badge.PEER)
    skill_badge = (badge.badge_type == Badge.SKILL)
    community_badge = (badge.badge_type == Badge.COMMUNITY)
    other_badge = (badge.badge_type == Badge.OTHER)
    submissions = badge.submissions.all().order_by(
        '-created_on')
    if request.user.is_authenticated():
    	user = request.user.get_profile()
    	applications = submissions.filter(author=user)
    awarded_user_ids = badge.awards.all().values('user_id')
    awarded_users = UserProfile.objects.filter(
        deleted=False, id__in=awarded_user_ids)
    related_projects = badge.groups.all()
    prerequisites = badge.prerequisites.all()
    other_badges_can_apply_for = badge.other_badges_can_apply_for()[:5]
    context = {
        'badge': badge,
        'is_eligible': is_eligible,
        'rubrics': rubrics,
        'peer_skill': peer_assessment and skill_badge,
        'peer_community': peer_assessment and community_badge,
        'other_badge': other_badge,
        'related_projects': related_projects,
        'prerequisites': prerequisites,
        'applications': applications,
        'other_badges_can_apply_for': other_badges_can_apply_for,
    }
    context.update(get_pagination_context(request, awarded_users,
        24, prefix='awarded_users_'))
    context.update(get_pagination_context(request, submissions,
        24, prefix='submissions_'))
    return render_to_response('badges/badge.html', context,
        context_instance=RequestContext(request))


def badges_list(request):
    badges = Badge.objects.all()
    return render_to_response('badges/badges_list.html',
        {'badges': badges},
        context_instance=RequestContext(request))


@login_required
def create_badge(request):
    if not request.user.is_superuser:
        raise http.Http404
    if request.method == 'POST':
        form = badge_forms.BadgeForm(request.POST)
        if form.is_valid():
            badge = form.save()
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
def create_submission(request, slug):
    badge = get_object_or_404(Badge, slug=slug,
        assessment_type=Badge.PEER, badge_type=Badge.SKILL)
    if not badge.is_eligible(request.user):
        messages.error(request,
            _('You are lacking one or more of the requirements.'))
        return http.HttpResponseRedirect(badge.get_absolute_url())
    user = request.user.get_profile()
    rubrics = badge.rubrics.all()
    related_projects = badge.groups.all()
    submission = None
    if request.method == 'POST':
        form = badge_forms.SubmissionForm(request.POST)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.badge = badge
            submission.author = user
            if 'show_preview' not in request.POST:
                submission.save()
                messages.success(request,
                    _('Submission created and out for review!'))
                return http.HttpResponseRedirect(submission.get_absolute_url())
        else:
            messages.error(request, _('Please correct errors below.'))
    else:
        form = badge_forms.SubmissionForm(instance=badge)

    context = {
        'form': form,
        'badge': badge,
        'rubrics': rubrics,
        'related_projects': related_projects,
    }
    return render_to_response('badges/submission_edit.html', context,
        context_instance=RequestContext(request))


def show_submission(request, slug, submission_id):
    submission = get_object_or_404(Submission, id=submission_id,
        badge__slug=slug)
    badge = submission.badge
    progress = badge.progress_for(submission.author)
    rubrics = badge.rubrics.all()
    assessments = Assessment.objects.filter(submission=submission_id)
    can_assess = True
    if request.user.is_authenticated():
        user = request.user.get_profile()
        has_assessed = Assessment.objects.filter(assessor=user,
            submission=submission)
        if has_assessed or user == submission.author:
            can_assess = False

    context = {
        'badge': badge,
        'submission': submission,
        'progress': progress,
        'rubrics': rubrics,
        'assessments': assessments,
        'can_assess': can_assess,
        }

    return render_to_response('badges/submission_show.html', context,
                              context_instance=RequestContext(request))


def submissions_list(request):
    submissions = Submission.objects.all()
    return render_to_response('badges/submissions_list.html',
        {'submissions': submissions},
        context_instance=RequestContext(request))


def matching_submissions(request, slug):
    badge = get_object_or_404(Badge, slug=slug)
    submissions = []
    pending = False
    if 'filter' in request.GET:
        filter_name = request.GET['filter']
        if filter_name == 'pending':
            submissions = badge.get_pending_submissions
            pending = True
        #TODO add more filters
    else:
        submissions = Submission.objects.filter(badge=badge)
    return render_to_response('badges/submissions_list.html',
        {'submissions': submissions,
         'badge': badge,
         'pending': pending},
        context_instance=RequestContext(request))

 
@login_required
def assess_submission(request, slug, submission_id):
    submission = get_object_or_404(Submission, id=submission_id,
        badge__slug=slug)
    rubrics = submission.badge.rubrics.all()
    badge = submission.badge
    user = request.user.get_profile()
    already_assessed = Assessment.objects.filter(assessor=user,
        submission=submission)

    if request.user == submission.author:
        messages.error(request, _('You cannot assess your own work.'))
        return http.HttpResponseRedirect(submission.get_absolute_url())
    if already_assessed:
        messages.error(request,
            _('You have already assessed this submission.'))
        return http.HttpResponseRedirect(submission.get_absolute_url())

    assessment = None
    rating_forms = []

    if request.method == 'POST':
        form = badge_forms.AssessmentForm(request.POST, prefix='assessment')
        if form.is_valid():
            assessment = form.save(commit=False)
            ratings = []
            valid_ratings = True
            for rubric in rubrics:
                rating_form = badge_forms.RatingForm(request.POST,
                    prefix="rubric%s_" % rubric.id)
                rating = rating_form.save(commit=False)
                rating.rubric = rubric
                if not rating_form.is_valid():
                    valid_ratings = False
                rating_forms.append((rubric, rating_form))
                ratings.append(rating)
            if valid_ratings and 'show_preview' not in request.POST:
                assessment.assessor = user
                assessment.assessed = submission.author
                assessment.badge = submission.badge
                assessment.submission = submission
                assessment.save()
                for rating in ratings:
                    rating.assessment = assessment
                    rating.save()
                messages.success(request,
                    _('Assessment saved. Thank you for your feedback!'))
                return http.HttpResponseRedirect(submission.get_absolute_url())
            if not valid_ratings:
                messages.error(request, _('Please correct errors below.'))
        else:
            messages.error(request, _('Please correct errors below.'))
    else:
        form = badge_forms.AssessmentForm(prefix='assessment')
        for rubric in rubrics:
            rating_form = badge_forms.RatingForm(
                prefix="rubric%s_" % rubric.id)
            rating_forms.append((rubric, rating_form))

    context = {
        'form': form,
        'submission': submission,
        'rubrics': rubrics,
        'badge': badge,
        'rating_forms': rating_forms,
    }
    return render_to_response('badges/assessment_edit.html', context,
                              context_instance=RequestContext(request))


def show_assessment(request, slug, assessment_id):
    assessment = get_object_or_404(Assessment, id=assessment_id,
        badge__slug=slug)
    if assessment.submission:
        return http.HttpResponseRedirect(assessment.submission.get_absolute_url())

    context = {
        'assessment': assessment,
        'badge': assessment.badge,
    }

    return render_to_response('badges/show_assessment.html', context,
                              context_instance=RequestContext(request))


@login_required
def create_assessment(request, slug):
    badge = get_object_or_404(Badge, slug=slug,
        assessment_type=Badge.PEER, badge_type=Badge.COMMUNITY)
    user = request.user.get_profile()
    rubrics = badge.rubrics.all()
    assessment = None
    if request.method == 'POST':
        form = badge_forms.PeerAssessmentForm(badge, user, request.POST)
        if form.is_valid():
            assessment = form.save(commit=False)
            if 'show_preview' not in request.POST:
                assessment.assessor = user
                assessment.assessed = form.cleaned_data['peer']
                assessment.badge = badge
                assessment.save()
                messages.success(request,
                    _('Thank you for giving a badge to your peer!'))
                return http.HttpResponseRedirect(assessment.get_absolute_url())
        else:
            messages.error(request, _('Please correct errors below.'))
    else:
        if 'peer' in request.GET:
            form = badge_forms.PeerAssessmentForm(
                badge, user, initial={'peer': request.GET['peer']})
        else:
            form = badge_forms.PeerAssessmentForm(
                badge, user)
        form = badge_forms.PeerAssessmentForm(badge, user)
    context = {
        'badge': badge,
        'assessment': assessment,
        'form': form,
        'rubrics': rubrics,
    }
    return render_to_response('badges/peer_assessment.html', context,
                              context_instance=RequestContext(request))


@login_required
def matching_peers(request, slug):
    badge = get_object_or_404(Badge, slug=slug,
        assessment_type=Badge.PEER, badge_type=Badge.COMMUNITY)
    if len(request.GET['term']) == 0:
        raise http.Http404
    peers = badge.get_peers(request.user.get_profile())
    matching_peers = peers.filter(username__icontains=request.GET['term'])
    json = simplejson.dumps([peer.username for peer in matching_peers])

    return http.HttpResponse(json, mimetype="application/json")


def show_user_awards(request, slug, username):
    badge = get_object_or_404(Badge, slug=slug)
    profile = get_object_or_404(UserProfile, username=username)
    awards_count = badge.awards.filter(user=profile).count()

    rubrics = badge.rubrics.all()
    peer_assessment = (badge.assessment_type == Badge.PEER)
    skill_badge = (badge.badge_type == Badge.SKILL)
    community_badge = (badge.badge_type == Badge.COMMUNITY)
    submissions = badge.submissions.filter(author=profile).order_by(
        '-created_on')
    progress = badge.progress_for(profile) if skill_badge else None
    assessments = badge.assessments.all().order_by(
        '-created_on')
    related_projects = badge.groups.all()
    prerequisites = badge.prerequisites.all()

    context = {
        'badge': badge,
        'profile': profile,
        'awards_count': awards_count,
        'rubrics': rubrics,
        'peer_skill': peer_assessment and skill_badge,
        'peer_community': peer_assessment and community_badge,
        'related_projects': related_projects,
        'prerequisites': prerequisites,
        'submissions': submissions,
        'assessments': assessments,
        'progress': progress,
    }
    return render_to_response('badges/show_user_awards.html', context,
                              context_instance=RequestContext(request))


def other_badges(request, slug):
    badge = get_object_or_404(Badge, slug=slug);
    try:
        first = max(1, int(request.GET['first']))
    except:
        first = 1
    try:
        last = max(first + 1, int(request.GET['last']))
    except:
        last = first + 1
    other_badges_can_apply = badge.other_badges_can_apply_for()
    total = other_badges_can_apply.count()
    items = other_badges_can_apply[first - 1: last]
    items_html = []
    for item in items:
        item_html = render_to_string('badges/_badge_item.html',
            {'badge': item}).strip()
        items_html.append(item_html)
    data = {
        'total': total,
        'items': items_html,
    }
    json = simplejson.dumps(data)
    return http.HttpResponse(json, mimetype="application/json")
