from django.contrib import auth
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_http_methods

import jingo

import registration.views

from users.models import authenticate 
from users.auth import users_login_begin, users_login_complete
from users.auth import OpenIDAuthError

def login_begin(request, registration=False):
    """Begin OpenID auth workflow."""
    try:
        return users_login_begin(request, registration)
    except OpenIDAuthError, exc:
        return jingo.render(request, 'dashboard/signin.html', {
            'error' : exc.message,
            'openid' : True
        }, status=403)

def login_complete(request):
    """Parse response from OpenID provider."""
    try:
        return users_login_complete(request)
    except OpenIDAuthError, exc:
        return jingo.render(request, 'dashboard/signin.html', {
            'error' : exc.message,
            'openid' : True
        }, status=403)

def login(request):
    """Log the user in."""
    if request.user.is_authenticated() or request.method == 'GET':
        return HttpResponseRedirect('/')
    if request.POST.get('openid_identifier', False):
        return login_begin(request)
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = authenticate(username=username, password=password)
    if user is not None and user.is_active:
        auth.login(request, user)
        return HttpResponseRedirect('/')
    return jingo.render(request, 'dashboard/signin.html', {
        'error': _('Incorrect login or password.'),
    })

def login_openid(request):
    """TODO: Render an OpenID login dialogue for those without JavaScript."""
    return jingo.render(request, 'users/login_openid.html')

def logout(request):
    """Destroy user session."""
    auth.logout(request)
    return HttpResponseRedirect('/')

def register(request):
    """Just punt to django-registration for now."""
    return registration.views.register(request)

def forgot(request):
    """Stub method."""
    return HttpResponseRedirect('/')
