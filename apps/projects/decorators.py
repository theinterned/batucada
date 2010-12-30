from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404

from projects.models import Project


def ownership_required(func):
    """
    Because I'm lazy, check here that the currently logged in user is
    the owner of the project specified by the ``slug`` kwarg. Return a
    403 response if they're not.
    """
    def decorator(*args, **kwargs):
        request = args[0]
        project = kwargs['slug']
        user = request.user.get_profile()
        project = get_object_or_404(Project, slug=project)
        if user != project.created_by:
            return HttpResponseForbidden()
        return func(*args, **kwargs)
    return decorator
