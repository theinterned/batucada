from django.contrib import auth
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_http_methods

import jingo

from users.models import authenticate
from users.forms import RegisterForm, OpenIDRegisterForm
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
    """Present user registration form and handle registrations."""
    form = None
    openid_form = None
    if request.method == 'POST':
        if request.POST.get('openid_identifier', False):
            openid_form = OpenIDRegisterForm(data=request.POST)
            if openid_form.is_valid():
                return login_begin(request, registration=True)
        else:
            form = RegisterForm(data=request.POST)
            if form.is_valid():
                user = form.save()
                auth.login(request, user)
                return HttpResponseRedirect('/')
    else:
        form = RegisterForm()
        openid_form = OpenIDRegisterForm()
    return jingo.render(request, 'users/register.html', {
        'form': form,
        'openid_form' : openid_form
    })

def register_openid(request):
    """Register with an OpenID (not a username / password)."""
    return HttpResponseRedirect('/')

def forgot(request):
    """Stub method."""
    return HttpResponseRedirect('/')
