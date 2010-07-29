import urllib

from django.contrib import auth
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
from openid.consumer.consumer import SUCCESS
from openid.consumer.discover import DiscoveryFailure
from openid.consumer.consumer import Consumer, SUCCESS, CANCEL, FAILURE
from openid.extensions import sreg

from django_openid_auth.auth import OpenIDBackend
from django_openid_auth.forms import OpenIDLoginForm
from django_openid_auth.models import UserOpenID
from django_openid_auth.views import make_consumer, render_openid_request, \
     parse_openid_response

from l10n.urlresolvers import reverse

def authenticate(username=None, password=None):
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
        if user.check_password(password):
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
        raise OpenIDAuthError(_("OpenID discovery error") + ": %s" % (str(exc),))

    openid_request.addExtension(
        sreg.SRegRequest(optional=['email', 'fullname', 'nickname']))

    viewname = 'users.views.login_complete'
    return_to = request.build_absolute_uri(reverse(viewname))
    if registration:
        return_to += ('?' in return_to) and '&' or '?'
        return_to += urllib.urlencode({
            'registration': registration
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
            'OpenID authentication failed') + ': %s' % openid_response.message
        )

    if openid_response.status == CANCEL:
        raise OpenIDAuthError(_('Authentication cancelled'))

    if openid_response.status != SUCCESS:
        assert False, "Unknown OpenID response type: %r" % openid_response.status

    user = auth.authenticate(openid_response=openid_response, request=request)
    if user is None:
        raise OpenIDAuthError(_('No user found with that OpenID.'))
    if not user.is_active:
        raise OpenIDAuthError(_('This account is not active.'))

    auth.login(request, user)
    return HttpResponseRedirect('/')


class CustomOpenIDBackend(OpenIDBackend):
    """
    Custom backend implementation. Create new accounts based on OpenID
    credentials *only* on registration, not on sign in attempts.
    """
    def authenticate(self, **kwargs):
        openid_response = kwargs.get('openid_response')

        if openid_response is None:
            return None

        if openid_response.status != SUCCESS:
            return None

        request = kwargs.get('request')

        if request is None:
            return None

        registering = request.GET.get('registration', False)

        try:
            user_openid = UserOpenID.objects.get(
                claimed_id__exact=openid_response.identity_url)
        except UserOpenID.DoesNotExist:
            if registering:
                user = self.create_user_from_openid(openid_response)
        
        return OpenIDBackend.authenticate(self, **kwargs)
