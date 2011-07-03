import logging

from django.db.utils import IntegrityError
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
        relationship = Relationship(source=profile, target_project=project)
        url = project.get_absolute_url()
    elif object_type == USER:
        user = get_object_or_404(UserProfile, username=slug)
        relationship = Relationship(source=profile, target_user=user)
        url = user.get_absolute_url()
    else:
        raise Http404
    try:
        relationship.save()
    except IntegrityError:
        if object_type == PROJECT:
            messages.error(
                request, _('You are already following this study group'))
        else:
            messages.error(request, _('You are already following this user'))
        log.warn("Attempt to create duplicate relationship: %s" % (
            relationship,))
    return HttpResponseRedirect(url)


@login_required
@require_http_methods(['POST'])
def unfollow(request, object_type, slug):
    profile = request.user.get_profile()
    if object_type == PROJECT:
        project = get_object_or_404(Project, slug=slug)
        # project.participants() includes project.organizers()
        if project.participants().filter(user=profile).exists():
            messages.error(request, _("You can't unfollow"))
        else:
            Relationship.objects.filter(
                source=profile, target_project=project).delete()
        url = project.get_absolute_url()
    elif object_type == USER:
        user = get_object_or_404(UserProfile, username=slug)
        Relationship.objects.filter(
            source=profile, target_user=user).delete()
        url = user.get_absolute_url()
    else:
        raise Http404
    return HttpResponseRedirect(url)
