import logging

from django.http import HttpResponseRedirect, Http404
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _

from relationships.models import Relationship
from projects.models import Project
from users.models import UserProfile
from users.decorators import login_required

from drumbeat import messages

log = logging.getLogger(__name__)

PROJECT = 'course'
USER = 'user'


@login_required
@require_http_methods(['POST'])
def follow(request, object_type, slug):
    profile = request.user.get_profile()
    if object_type == PROJECT:
        project = get_object_or_404(Project, slug=slug)
        relationship, created = Relationship.objects.get_or_create(
            source=profile, target_project=project)
        url = project.get_absolute_url()
    elif object_type == USER:
        user = get_object_or_404(UserProfile, username=slug)
        relationship, created = Relationship.objects.get_or_create(
            source=profile, target_user=user)
        url = user.get_absolute_url()
    else:
        raise Http404
    relationship.deleted = False
    relationship.save()
    return HttpResponseRedirect(url)


@login_required
@require_http_methods(['POST'])
def unfollow(request, object_type, slug):
    profile = request.user.get_profile()
    if object_type == PROJECT:
        project = get_object_or_404(Project, slug=slug)
        url = project.get_absolute_url()
        # project.participants() includes project.organizers()
        if project.participants().filter(user=profile).exists():
            messages.error(request, _("You can't unfollow"))
            return HttpResponseRedirect(url)
        else:
            relationship = get_object_or_404(Relationship, source=profile,
                target_project=project)
    elif object_type == USER:
        user = get_object_or_404(UserProfile, username=slug)
        relationship = get_object_or_404(Relationship, source=profile,
            target_user=user)
        url = user.get_absolute_url()
    else:
        raise Http404
    relationship.deleted = True
    relationship.save()
    return HttpResponseRedirect(url)
