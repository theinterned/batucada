from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _

import jingo
from django_openid_auth.forms import OpenIDLoginForm
from profiles import utils

from l10n.urlresolvers import reverse
from users.models import Profile
from users.forms import RegisterForm, LoginForm
from users.auth import users_login_begin, users_login_complete, authenticate
from users.auth import OpenIDAuthError
from users.decorators import anonymous_only
from relationships.models import UserRelationship

def login_begin(request, registration=False):
    """Begin OpenID auth workflow."""
    try:
        return users_login_begin(request, registration)
    except OpenIDAuthError, exc:
        return jingo.render(request, 'users/login_openid.html', {
            'error' : exc.message,
            'form' : OpenIDLoginForm()
        }, status=403)

def login_complete(request):
    """Parse response from OpenID provider."""
    try:
        return users_login_complete(request)
    except OpenIDAuthError, exc:
        return jingo.render(request, 'users/login_openid.html', {
            'error' : exc.message,
            'form' : OpenIDLoginForm()
        }, status=403)

@anonymous_only
def login(request):
    """Log the user in."""
    if request.user.is_authenticated() or request.method == 'GET':
        return HttpResponseRedirect('/')

    form = LoginForm(data=request.POST)
    if not form.is_valid():
        return jingo.render(request, 'dashboard/signin.html', {
            'form' : form
        })
    username = form.cleaned_data['username']
    password = form.cleaned_data['password']
    user = authenticate(username=username, password=password)

    if user is not None and user.is_active:
        auth.login(request, user)
        return HttpResponseRedirect('/')

    return jingo.render(request, 'dashboard/signin.html', {
        'form' : form,
        'error': _('Incorrect login or password.'),
    })

@anonymous_only
def login_openid(request):
    """Handle OpenID logins."""
    if request.method == 'GET':
        return jingo.render(request, 'users/login_openid.html', {
            'form': OpenIDLoginForm()
        })
        
    form = OpenIDLoginForm(data=request.POST)
    if form.is_valid():
        return login_begin(request)
    
    return jingo.render(request, 'users/login_openid.html', {
        'form' : form
    })

@login_required
def logout(request):
    """Destroy user session."""
    auth.logout(request)
    return HttpResponseRedirect('/')

@anonymous_only
def register(request):
    """Present user registration form and handle registrations."""
    if request.method == 'POST':
        form = RegisterForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            auth.login(request, user)
            return HttpResponseRedirect('/')
    return jingo.render(request, 'users/register.html', {
        'form': RegisterForm(),
    })

@anonymous_only
def register_openid(request):
    """Handle OpenID registrations."""
    form = OpenIDLoginForm()
    if request.method == 'POST':
        form = OpenIDLoginForm(data=request.POST)
        if form.is_valid():
            return login_begin(request, registration=True)
    return jingo.render(request, 'users/register_openid.html', {
        'form' : form
    })

@anonymous_only
def forgot(request):
    """Stub method."""
    return HttpResponseRedirect('/')

@login_required
def profile(request):
    """Save profile."""
    user = User.objects.get(username__exact=request.user.username)
    if request.method == 'POST':
        user.first_name = request.POST['first_name']
        user.last_name = request.POST['last_name']
        user.save()

        form_class = utils.get_profile_form()
        try:
            profile = user.get_profile()
            form = form_class(data=request.POST, instance=profile)
            if form.is_valid():
                form.save()
        except Profile.DoesNotExist:
            form = form_class(data=request.POST)
            if form.is_valid():
                profile = form.save(commit=False)
                profile.user = request.user
                profile.save()
        return HttpResponseRedirect(reverse('users.views.profile_detail',
                                            kwargs={'username':user.username}))
    profile = user.get_profile()
    form_class = utils.get_profile_form()
    form = form_class(instance=profile)
    return jingo.render(request, 'users/profile_edit.html', {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'form': form,
    })

@login_required
def profile_detail(request, username):
    user = User.objects.get(username__exact=username)
    return jingo.render(request, 'users/profile_detail.html', {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'profile': user.get_profile()
    })

@login_required
def profile_create(request):
    user = User.objects.get(username__exact=request.user.username)
    try:
        profile = user.get_profile()
        return HttpResponseRedirect(reverse('users.views.profile_edit',))
    except Profile.DoesNotExist:
        form_class = utils.get_profile_form()
        form = form_class()
        return jingo.render(request, 'users/profile_edit.html', {
            'user' : user,
            'form' : form,
        })

@login_required
def user_list(request):
    """Display a list of users on the site. TODO: Paginate."""
    users = User.objects.exclude(id__exact=request.user.id)
    following = UserRelationship.get_relationships_from(request.user)
    return jingo.render(request, 'users/user_list.html', {
        'heading' : _('Users'),
        'users' : users,
        'following' : following
    })
