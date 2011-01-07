from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth import decorators as auth_decorators
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _

from drumbeat import messages
from users.models import UserProfile


def anonymous_only(func):
    """
    Opposite of ``django.contrib.auth.decorators.login_required``. This
    decorator is for views that redirect users to the redirect field name
    if they are already logged in.
    """

    def decorator(*args, **kwargs):
        request = args[0]
        if request.user.is_authenticated():
            messages.info(request,
                          _("You are already logged into an account."))
            return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
        return func(*args, **kwargs)
    return decorator


def login_required(func=None, redirect_field_name=REDIRECT_FIELD_NAME,
                   profile_required=True):
    """
    Custom implementation of ``django.contrib.auth.decorators.login_required``.
    This version has an optional parameter, ``profile_required`` which, if
    True, will check that a user is both authenticated and has a profile. This
    is useful so that the create profile page can load successfully, but a user
    will still be locked out of other views.
    """
    if profile_required:
        test = lambda u: (u.is_authenticated() and
                          len(UserProfile.objects.filter(user=u)) > 0)
    else:
        test = lambda u: u.is_authenticated()
    actual_decorator = auth_decorators.user_passes_test(
        test, redirect_field_name=redirect_field_name,
    )
    if func:
        return actual_decorator(func)
    return actual_decorator
