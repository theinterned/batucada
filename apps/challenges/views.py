import logging

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from challenges.models import Challenge, Submission
from projects.models import Project

from users.decorators import login_required

@login_required
def create_challenge(request, project_id):
    pass

def show_challenge(request, slug):
    challenge = get_object_or_404(Challenge, slug=slug)

    context = {
        'challenge' : challenge
    }

    return render_to_response('challenges/challenge.html', context,
                              context_instance=RequestContext(request))
    
def create_submission(request):
    pass
