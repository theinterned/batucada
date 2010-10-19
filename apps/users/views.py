from django.conf import settings
from django.contrib import auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_http_methods
from django.shortcuts import render_to_response
from django.template import RequestContext

from django_openid_auth.forms import OpenIDLoginForm

from users.mail import send_reset_email, send_registration_email
from users.models import ConfirmationToken, unique_confirmation_token
from users.forms import (RegisterForm, LoginForm, ForgotPasswordForm,
                         ResetPasswordForm)
from users.auth import users_login_begin, users_login_complete, authenticate
from users.auth import OpenIDAuthError
from users.decorators import anonymous_only

def login_begin(request, registration=False):
    """Begin OpenID auth workflow."""
    try:
        return users_login_begin(request, registration)
    except OpenIDAuthError, exc:
        response = render_to_response('users/login_openid.html', {
            'error': exc.message,
            'form': OpenIDLoginForm()
        }, context_instance=RequestContext(request))
        response.status_code = 403
        return response

def login_complete(request):
    """Parse response from OpenID provider."""
    try:
        return users_login_complete(request)
    except OpenIDAuthError, exc:
        response = render_to_response('users/login_openid.html', {
            'error': exc.message,
            'form': OpenIDLoginForm()
        }, context_instance=RequestContext(request))
        response.status_code = 403
        return response

@anonymous_only
def login(request):
    """Log the user in."""
    if request.method == 'GET':
        return render_to_response('users/signin.html', {
            'form': LoginForm(),
        }, context_instance=RequestContext(request))

    form = LoginForm(data=request.POST)
    if not form.is_valid():
        return render_to_response('dashboard/signin.html', {
            'form' : form
        }, context_instance=RequestContext(request))
    username = form.cleaned_data['username']
    password = form.cleaned_data['password']
    user = authenticate(username=username, password=password)

    if user is not None and user.is_active:
        auth.login(request, user)
        return HttpResponseRedirect(reverse('dashboard_index'))

    return render_to_response('dashboard/signin.html', {
        'form' : form,
        'error': _('Incorrect login or password.'),
    }, context_instance=RequestContext(request))

@anonymous_only
def login_openid(request):
    """Handle OpenID logins."""
    if request.method == 'GET':
        return render_to_response('users/login_openid.html', {
            'form': OpenIDLoginForm()
        }, context_instance=RequestContext(request))
        
    form = OpenIDLoginForm(data=request.POST)
    if form.is_valid():
        return login_begin(request)
    
    return render_to_response('users/login_openid.html', {
        'form' : form
    }, context_instance=RequestContext(request))

@login_required
def logout(request):
    """Destroy user session."""
    auth.logout(request)
    return HttpResponseRedirect(reverse('dashboard_index'))

@anonymous_only
def register(request):
    """Present user registration form and handle registrations."""
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            if not settings.DEBUG:
                user.is_active = False
            user.save()
            if settings.DEBUG:
                user = authenticate(username=user.username, force=True)
                auth.login(request, user)
            else:
                token = unique_confirmation_token(user)
                send_registration_email(user, token.plaintext, 
                                        request.build_absolute_uri)
                messages.add_message(request, messages.INFO,
                    _("""Thanks! We have sent an email to %(email)s with
                    instructions for completing your registration.""" % {
                          'email': user.email }))
            return HttpResponseRedirect(reverse('dashboard_index'))
    return render_to_response('users/register.html', {
        'form': form,
    }, context_instance=RequestContext(request))

@anonymous_only
def register_openid(request):
    """Handle OpenID registrations."""
    form = OpenIDLoginForm()
    if request.method == 'POST':
        form = OpenIDLoginForm(data=request.POST)
        if form.is_valid():
            return login_begin(request, registration=True)
    return render_to_response('users/register_openid.html', {
        'form' : form
    }, context_instance=RequestContext(request))

@login_required
def user_list(request):
    """Display a list of users on the site. TODO: Paginate."""
    users = User.objects.exclude(id__exact=request.user.id)
    return render_to_response('users/user_list.html', {
        'heading' : _('Users'),
        'users' : users,
        'following' : [user.id for user in request.user.following()]
    }, context_instance=RequestContext(request))

@anonymous_only
def forgot_password(request):
    """Allow users to reset their password by validating email ownership."""
    if request.method == 'GET':
        return render_to_response('users/forgot_password.html', {
            'form': ForgotPasswordForm()
        }, context_instance=RequestContext(request))
    error = None
    form = ForgotPasswordForm(request.POST)
    if not form.is_valid():
        return render_to_response('users/forgot_password.html', {
            form: 'form'
        }, context_instance=RequestContext(request))
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
        return HttpResponseRedirect(reverse('dashboard_index'))
    except User.DoesNotExist:
        error = _('Email address not found.')

    return render_to_response('users/forgot_password.html', {
        'form': form,
        'error': error
    }, context_instance=RequestContext(request))

@anonymous_only
def reset_password(request, token, username):
    """Reset users password."""
    form = ResetPasswordForm(data=request.POST)
    if not form.is_valid():
        return render_to_response('users/reset_password.html', {
            'form': form,
            'token': token,
            'username': username
        }, context_instance=RequestContext(request))
    password = form.cleaned_data['password']
    user = User.objects.get(username=form.cleaned_data['username'])
    user.set_password(password)
    user.save()
    ConfirmationToken.objects.filter(user__exact=user.id).delete()
    messages.add_message(request, messages.INFO,
                         _('Your password has been reset.'))

    user = authenticate(username=user.username, password=password)
    if user is not None and user.is_active:
        auth.login(request, user)
    return HttpResponseRedirect(reverse('dashboard_index'))

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
    return render_to_response('users/reset_password.html', {
        'form': form,
        'error': error,
        'token': token,
        'username': username
    }, context_instance=RequestContext(request))

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
        ConfirmationToken.objects.filter(user__exact=user.id).delete()
        messages.add_message(
            request,
            messages.INFO,
            _('Congratulations. Your have completed your registration.')
        )
    except:
        return render_to_response('users/register.html', {
            'form': RegisterForm(),
            'error': _('Confirmation failed. Invalid token or username.'),
        }, context_instance=RequestContext(request))

    return HttpResponseRedirect(reverse('dashboard_index'))
