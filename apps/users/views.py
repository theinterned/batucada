from django.contrib import auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, Http404
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_http_methods

import jingo
from django_openid_auth.forms import OpenIDLoginForm
from profiles import utils

from l10n.urlresolvers import reverse
from users.mail import send_reset_email, send_registration_email
from users.models import Profile, ConfirmationToken, unique_confirmation_token
from users.forms import (RegisterForm, LoginForm, ForgotPasswordForm,
                         ResetPasswordForm)
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
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(data=request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            token = unique_confirmation_token(user)
            send_registration_email(user, token.plaintext, 
                                    request.build_absolute_uri)
            messages.add_message(request, messages.INFO,
                _("""Thanks! We have sent an email to %(email)s with
                instructions for completing your registration.""" % {
                      'email': user.email }))
            return HttpResponseRedirect('/')
    return jingo.render(request, 'users/register.html', {
        'form': form,
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

@login_required
def profile(request):
    """Save profile."""
    user = User.objects.get(username__exact=request.user.username)
    if request.method == 'POST':
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
    try:
        profile = user.get_profile()
    except Profile.DoesNotExist:
        return HttpResponseRedirect(reverse('users.views.profile_create'))
    
    form_class = utils.get_profile_form()
    form = form_class(instance=profile)
    return jingo.render(request, 'users/profile_edit.html', {
        'form': form,
    })

@login_required
def profile_detail(request, username):
    user = User.objects.get(username__exact=username)
    try:
        profile = user.get_profile()
    except Profile.DoesNotExist:
        raise Http404
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

@anonymous_only
def forgot_password(request):
    """Allow users to reset their password by validating email ownership."""
    if request.method == 'GET':
        return jingo.render(request, 'users/forgot_password.html', {
            'form': ForgotPasswordForm()
        })
    error = None
    form = ForgotPasswordForm(request.POST)
    if not form.is_valid():
        return jingo.render(request, 'users/forgot_password.html', {
            form: 'form'
        })
    try:
        email = form.cleaned_data['email']
        user = User.objects.get(email__exact=email)
        token = unique_confirmation_token(user)
        send_reset_email(user, token.plaintext, request.build_absolute_uri)
        messages.add_message(
            request,
            messages.INFO,
            _("""An email has been sent to %(email)s with instructions
            for resetting your password.""" % dict(email=email))
        )
        return HttpResponseRedirect(reverse('dashboard.views.index'))
    except User.DoesNotExist:
        error = _('Email address not found.')

    return jingo.render(request, 'users/forgot_password.html', {
        'form': form,
        'error': error
    })

@anonymous_only
def reset_password(request, token, username):
    """Reset users password."""
    form = ResetPasswordForm(data=request.POST)
    if not form.is_valid():
        return jingo.render(request, 'users/reset_password.html', {
            'form': form,
            'token': token,
            'username': username
        })
    password = form.cleaned_data['password']
    user = User.objects.get(username=form.cleaned_data['username'])
    user.set_password(password)
    user.save()

    # clean up
    ConfirmationToken.objects.filter(user__exact=user.id).delete()

    messages.add_message(request, messages.INFO,
                         _('Your password has been reset.'))

    user = authenticate(username=user.username, password=password)
    if user is not None and user.is_active:
        auth.login(request, user)
    return HttpResponseRedirect('/')

@anonymous_only
def reset_password_form(request, token, username):
    """Render the reset password form, validating username and token."""
    if request.method == 'POST':
        return reset_password(request, token, username)

    error = None
    try:
        user = User.objects.get(username__exact=username)
        token_obj = ConfirmationToken.objects.get(user__exact=user.id)
        if not token_obj.check_token(token):
            raise
    except:
        error = 'Sorry, invalid user or token'

    form = ResetPasswordForm()
    return jingo.render(request, 'users/reset_password.html', {
        'form': form,
        'error': error,
        'token': token,
        'username': username
    })

@anonymous_only
def confirm_registration(request, token, username):
    """Confirm a users registration."""
    try:
        user = User.objects.get(username__exact=username)
        token_obj = ConfirmationToken.objects.get(user__exact=user.id)
        if not token_obj.check_token(token):
            raise
        user.is_active = True
        user.save()
        user = authenticate(username=user.username, force=True)
        auth.login(request, user)
        messages.add_message(
            request,
            messages.INFO,
            _('Congratulations. Your have completed your registration.')
        )
    except:
        return jingo.render(request, 'users/register.html', {
            'form': RegisterForm(),
            'error': _('Confirmation failed. Invalid token or username.'),
        })

    return HttpResponseRedirect('/')
