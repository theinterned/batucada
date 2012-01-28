from django.http import HttpResponseForbidden
from django.utils.translation import ugettext as _

from reviews.models import Reviewer


def reviewer_required(func):
    def decorated(*args, **kwargs):
        request = args[0]
        if request.user.is_authenticated():
            profile = request.user.get_profile()
            if Reviewer.objects.filter(user=profile).exists():
                return func(*args, **kwargs)
        return HttpResponseForbidden(_("You need to be a reviewer."))
    return decorated
