from django.conf import settings
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _

from projects.models import Project


def organizer_required(func):
    """
    Return a 403 response if the user is not organizing the project
    specified by the ``slug`` kwarg.
    """

    def decorator(*args, **kwargs):
        request = args[0]
        project = kwargs['slug']
        project = get_object_or_404(Project, slug=project)
        if not project.is_organizing(request.user):
            msg = _("You are not organizing this %s")
            return HttpResponseForbidden(msg % project.kind.lower())
        return func(*args, **kwargs)
    return decorator


def participation_required(func):
    """
    Return a 403 response if the user is not participating in the project
    specified by the ``slug`` kwarg.
    """
    def decorator(*args, **kwargs):
        request = args[0]
        project = kwargs['slug']
        project = get_object_or_404(Project, slug=project)
        if not project.is_participating(request.user):
            msg = _("You are not participating in this %s")
            return HttpResponseForbidden(msg % project.kind.lower())
        return func(*args, **kwargs)
    return decorator

def can_view_metric_detail(func):
    """
    Limited people can see the detailed metrics.
    """
    def decorator(*args, **kwargs):
        request = args[0]
        project = kwargs['slug']
        project = get_object_or_404(Project, slug=project)
        if not (request.user.username in settings.STATISTICS_COURSE_CAN_VIEW_CSV or request.user.is_superuser):
            msg = _("You are not authorized to view these detailed statistics.")
            return HttpResponseForbidden(msg)
        return func(*args, **kwargs)
    return decorator

def can_view_metric_overview(func):
    """
    Allow certain people to view metrics of courses for the dark launch/slow
    rollout of this feature.
    """
    def decorator(*args, **kwargs):
        request = args[0]
        project = kwargs['slug']
        project = get_object_or_404(Project, slug=project)
        if not (request.user.username in settings.STATISTICS_COURSE_CAN_VIEW_CSV or request.user.is_superuser):
            msg = _("You are not authorized to view these overview statistics.")
            print project.is_organizing(request.user)
            return HttpResponseForbidden(msg)
        return func(*args, **kwargs)
    return decorator