from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404

from relationships.models import Relationship
from projects.models import Project
from users.models import UserProfile


@login_required
@require_http_methods(['POST'])
def follow(request, object_type, slug):
    profile = request.user.get_profile()
    if object_type == 'project':
        project = get_object_or_404(Project, slug=slug)
        Relationship(source=profile, target_project=project).save()
    elif object_type == 'user':
        user = get_object_or_404(UserProfile, username=slug)
        Relationship(source=profile, target_user=user).save()
    else:
        raise Http404
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


@login_required
@require_http_methods(['POST'])
def unfollow(request, object_type, slug):
    profile = request.user.get_profile()
    if object_type == 'project':
        project = get_object_or_404(Project, slug=slug)
        Relationship.objects.filter(
            source=profile, target_project=project).delete()
    elif object_type == 'user':
        user = get_object_or_404(UserProfile, username=slug)
        Relationship.objects.filter(
            source=profile, target_user=user).delete()
    else:
        raise Http404
    return HttpResponseRedirect(request.META['HTTP_REFERER'])
