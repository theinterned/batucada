import logging

from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.urlresolvers import reverse
from django.db.utils import IntegrityError
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render_to_response
from django.utils.translation import ugettext as _
from django.template import RequestContext

from challenges.models import Challenge, Submission, Judge
from challenges.forms import ChallengeForm, SubmissionForm, JudgeForm
from projects.models import Project

from drumbeat import messages
from users.decorators import login_required

log = logging.getLogger(__name__)

@login_required
def create_challenge(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    user = request.user.get_profile()
    
    if request.method == 'POST':
        form = ChallengeForm(request.POST)
        if form.is_valid():
            challenge = form.save(commit=False)
            challenge.created_by = user
            challenge.project = project
            challenge.save()

            messages.success(request, _('Your new challenge has been created.'))
            return HttpResponseRedirect(reverse('challenges_show', kwargs={
                'slug': challenge.slug,
                }))
        else:
            messages.error(request, _('Unable to create your challenge.'))
    else:
        form = ChallengeForm()

    context = {
        'form': form,
        'project': project,
    }
    return render_to_response('challenges/challenge_edit.html', context,
                              context_instance=RequestContext(request))

def show_challenge(request, slug):
    challenge = get_object_or_404(Challenge, slug=slug)

    submission_set = challenge.submission_set.all().order_by('-created_on')
    paginator = Paginator(submission_set, 10)

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        submissions = paginator.page(page)
    except (EmptyPage, InvalidPage):
        submissions = paginator.page(paginator.num_pages)

    nsubmissions = challenge.submission_set.all().count()
    
    context = {
        'challenge' : challenge,
        'submissions' : submissions,
        'nsubmissions' : nsubmissions,
    }

    return render_to_response('challenges/challenge.html', context,
                              context_instance=RequestContext(request))

@login_required
def create_submission(request, slug):
    challenge = get_object_or_404(Challenge, slug=slug)
    if not challenge.is_active():
        return HttpResponseForbidden()
    
    user = request.user.get_profile()

    if request.method == 'POST':
        form = SubmissionForm(request.POST)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.created_by = user
            submission.save()

            submission.challenge.add(challenge)
            
            messages.success(request, _('Your submission has been created'))

            return HttpResponseRedirect(reverse('challenges_show', kwargs={
                'slug': challenge.slug,
                }))
        else:
            messages.error(request, _('Unable to create your submission'))
    else:
        form = SubmissionForm()

    context = {
        'form' : form,
        'challenge' : challenge
    }

    return render_to_response('challenges/submission_create.html', context,
                              context_instance=RequestContext(request))

@login_required
def challenge_judges(request, slug):
    challenge = get_object_or_404(Challenge, slug=slug)

    if request.method == 'POST':
        form = JudgeForm(request.POST)
        if form.is_valid():
            judge = form.save(commit=False)
            judge.challenge = challenge

            try:
                judge.save()
                messages.success(request, _('Judge has been added'))
            except IntegrityError:
                messages.error(request, _('User is already a judge'))


            return HttpResponseRedirect(reverse('challenges_judges', kwargs={
                'slug' : challenge.slug,
                }))
        else:
            messages.error(request, _('Unable to add judge.'))
    else:
        form = JudgeForm()

    judges = Judge.objects.filter( challenge=challenge )

    context = {
        'challenge' : challenge,
        'form' : form,
        'judges' : judges,
    }

    return render_to_response('challenges/challenge_judges.html', context,
                              context_instance=RequestContext(request))


@login_required
def challenge_judges_delete(request, slug, judge):
    if request.method == 'POST':
        challenge = get_object_or_404(Challenge, slug=slug)
        judge = get_object_or_404(Judge, pk=judge)
        if judge.challenge != challenge:
            return HttpResponseForbidden()
        judge.delete()
        messages.success(request, _('Judge removed.'))
    return HttpResponseRedirect(reverse('challenges_judges',kwargs={
                'slug': challenge.slug,
                }))
    
