from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _

from schools.models import School


def school_organizer_required(func):
    """
    Return a 403 response if they're not school organizers.
    """

    def decorator(*args, **kwargs):
        request = args[0]
        slug = kwargs['slug']
        user = request.user.get_profile()
        school = get_object_or_404(School, slug=slug)
        is_organizer = school.organizers.filter(id=user.id).exists()
        if not is_organizer and not user.user.is_superuser:
            return HttpResponseForbidden(_("You are not school organizer"))
        return func(*args, **kwargs)
    return decorator
