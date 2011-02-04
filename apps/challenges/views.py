import logging

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.utils.translation import ugettext as _
from django.template import RequestContext

from challenges.models import Challenge, Submission
from challenges.forms import ChallengeForm, SubmissionForm
from projects.models import Project

from drumbeat import messages
from users.decorators import login_required

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

    context = {
        'challenge' : challenge
    }

    return render_to_response('challenges/challenge.html', context,
                              context_instance=RequestContext(request))
    
def create_submission(request, slug):
    challenge = get_object_or_404(Challenge, slug=slug)
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
