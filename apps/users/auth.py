import urllib

from django.contrib import auth
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
from openid.consumer.discover import DiscoveryFailure
from openid.consumer.consumer import SUCCESS, CANCEL, FAILURE
from openid.extensions import sreg, ax

from django_openid_auth.forms import OpenIDLoginForm
from django_openid_auth.views import make_consumer, render_openid_request, \
     parse_openid_response

ax_attributes = {
    'email': ('http://axschema.org/contact/email', True),
    'username': ('http://axschema.org/namePerson/friendly', True),
    'first_name': ('http://axschema.org/namePerson/first', True),
    'last_name': ('http://axschema.org/namePerson/last', True),
}


def authenticate(username=None, password=None, force=False):
    """
    Allow model backed user objects to support authentication by
    email / password as well as username / password.
    """
    backend = 'django.contrib.auth.backends.ModelBackend'
    try:
        if '@' in username:
            kwargs = dict(email=username)
        else:
            kwargs = dict(username=username)
        user = User.objects.get(**kwargs)
        if force or user.check_password(password):
            user.backend = backend
            return user
    except User.DoesNotExist:
        return None


class OpenIDAuthError(Exception):
    """Exception raised for OpenID authentication errors."""

    def __init__(self, message):
        self.message = message


def users_login_begin(request, registration=False):
    """
    Begin an OpenID auth request. We have to use our own instead of
    ``django_openid_auth.views.login_begin`` so that we can modify the
    ``return_to`` parameter to reference our own implementation of
    ``django_openid_auth.views.login_complete`` which distinguishes
    between login attempts and registrations.
    """
    login_form = OpenIDLoginForm(data=request.POST)
    if not login_form.is_valid():
        raise OpenIDAuthError(_('Invalid OpenID Identifier'))
    openid_url = login_form.cleaned_data['openid_identifier']

    consumer = make_consumer(request)
    try:
        openid_request = consumer.begin(openid_url)
    except DiscoveryFailure, exc:
        msg = _("OpenID discovery error") + ": %s" % (str(exc),)
        raise OpenIDAuthError(msg)

    openid_request.addExtension(
        sreg.SRegRequest(required=['email', 'fullname']))

    ax_request = ax.FetchRequest()
    for key, val in ax_attributes.iteritems():
        ax_request.add(ax.AttrInfo(val[0], alias=key, required=val[1]))
    openid_request.addExtension(ax_request)

    viewname = 'users_login_complete'
    return_to = request.build_absolute_uri(reverse(viewname))
    if registration:
        return_to += ('?' in return_to) and '&' or '?'
        return_to += urllib.urlencode({
            'registration': registration,
        })
    return render_openid_request(request, openid_request, return_to)


def users_login_complete(request):
    """
    Complete OpenID auth request. We use this instead of
    ``django_openid_auth.views.login_complete`` so we can pass request
    info to our backend ``authenticate`` method, thereby distinguishing
    between login attempts and registrations.
    """
    openid_response = parse_openid_response(request)
    if not openid_response:
        raise OpenIDAuthError(_('This is an OpenID relying party endpoint'))

    if openid_response.status == FAILURE:
        raise OpenIDAuthError(_(
            'OpenID authentication failed') + ': %s' % openid_response.message)

    if openid_response.status == CANCEL:
        raise OpenIDAuthError(_('Authentication cancelled'))

    if openid_response.status != SUCCESS:
        msg = _("Unknown response type: %r" % openid_response.status)
        raise OpenIDAuthError(msg)

    user = auth.authenticate(openid_response=openid_response, request=request)
    if user is None:
        raise OpenIDAuthError(_('No user found with that OpenID.'))
    if not user.is_active:
        raise OpenIDAuthError(_('This account is not active.'))

    auth.login(request, user)
    return HttpResponseRedirect('/')
