import logging

from django.contrib import auth
from django.contrib.auth import views as auth_views
from django.contrib.auth import forms as auth_forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from django_openid_auth.forms import OpenIDLoginForm

from users import forms
from users.auth import users_login_begin, users_login_complete
from users.auth import OpenIDAuthError
from users.models import UserProfile
from users.decorators import anonymous_only

from drumbeat import messages

log = logging.getLogger(__name__)


def login_begin(request, registration=False):
    """Begin OpenID auth workflow."""
    try:
        request.session['registration'] = registration
        return users_login_begin(request, registration)
    except OpenIDAuthError, exc:
        template = lambda r: (r and 'users/register_openid.html'
                              or 'users/login_openid.html')
        response = render_to_response(template(registration), {
            'error': exc.message,
            'form': OpenIDLoginForm(),
        }, context_instance=RequestContext(request))
        response.status_code = 403
        return response


def login_complete(request):
    """Parse response from OpenID provider."""
    try:
        return users_login_complete(request)
    except OpenIDAuthError, exc:
        if request.session.get('registration', False):
            template = 'users/register_openid.html'
        else:
            template = 'users/login_openid.html'
        try:
            del request.session['registration']
        except KeyError:
            pass
        response = render_to_response(template, {
            'error': exc.message,
            'form': OpenIDLoginForm(),
        }, context_instance=RequestContext(request))
        response.status_code = 403
        return response


@anonymous_only
def login(request):
    """Log the user in. Lifted most of this code from zamboni."""
    logout(request)

    r = auth_views.login(request, template_name='users/signin.html')

    if isinstance(r, HttpResponseRedirect):
        # Succsesful log in according to django.  Now we do our checks.  I do
        # the checks here instead of the form's clean() because I want to use
        # the messages framework and it's not available in the request there
        user = request.user.get_profile()

        if user.confirmation_code:
            logout(request)
            log.info(u'Attempt to log in with unconfirmed account (%s)' % user)
            msg1 = _(('A link to activate your user account was sent by email '
                      'to your address {0}. You have to click it before you '
                      'can log in.').format(user.email))
            url = request.build_absolute_uri(
                reverse('users_confirm_resend',
                        kwargs=dict(username=user.username)))
            msg2 = _(('If you did not receive the confirmation email, make '
                      'sure your email service did not mark it as "junk '
                      'mail" or "spam". If you need to, you can have us '
                      '<a href="%s">resend the confirmation message</a> '
                      'to your email address mentioned above.') % url)
            messages.error(request, msg1)
            messages.info(request, msg2, safe=True)
            return render_to_response('users/signin.html', {
                'form': auth_forms.AuthenticationForm(),
            }, context_instance=RequestContext(request))

    elif 'username' in request.POST:
        # Hitting POST directly because cleaned_data doesn't exist
        user = UserProfile.objects.filter(email=request.POST['username'])

    return r


@anonymous_only
def login_openid(request):
    """Handle OpenID logins."""
    if request.method == 'GET':
        return render_to_response('users/login_openid.html', {
            'form': OpenIDLoginForm(),
        }, context_instance=RequestContext(request))

    form = OpenIDLoginForm(data=request.POST)
    if form.is_valid():
        return login_begin(request)

    return render_to_response('users/login_openid.html', {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def logout(request):
    """Destroy user session."""
    auth.logout(request)
    return HttpResponseRedirect(reverse('dashboard_index'))


@anonymous_only
def register(request):
    """Present user registration form and handle registrations."""
    if request.method == 'POST':
        form = forms.RegisterForm(data=request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.generate_confirmation_code()
            user.save()
            user.create_django_user()

            log.info(u"Registered new account for user (%s)", user)

            messages.success(request, _('Congratulations! Your user account '
                                        'was successfully created.'))
            path = reverse('users_confirm_registration', kwargs={
                'username': user.username,
                'token': user.confirmation_code,
            })
            url = request.build_absolute_uri(path)
            user.email_confirmation_code(url)
            msg = _('Thanks! We have sent an email to {0} with '
                    'instructions for completing your '
                    'registration.').format(user.email)
            messages.info(request, msg)

            return HttpResponseRedirect(reverse('dashboard_index'))
        else:
            messages.error(request, _('There are errors in this form. Please '
                                      'correct them and resubmit.'))
    else:
        form = forms.RegisterForm()
    return render_to_response('users/register.html', {
        'form': form,
    }, context_instance=RequestContext(request))


@anonymous_only
def register_openid(request):
    """Handle OpenID registrations."""
    if request.method == 'POST':
        form = OpenIDLoginForm(data=request.POST)
        if form.is_valid():
            return login_begin(request, registration=True)
    else:
        form = OpenIDLoginForm()
    return render_to_response('users/register_openid.html', {
        'form': form,
    }, context_instance=RequestContext(request))


def user_list(request):
    """Display a list of users on the site. TODO: Paginate."""
    users = User.objects.exclude(id__exact=request.user.id)
    following = []
    object_type = None
    if request.user.is_authenticated():
        following = [user.id for user in request.user.following()]
        object_type = ContentType.objects.get_for_model(request.user)
    return render_to_response('users/user_list.html', {
        'heading': _('Users'),
        'users': users,
        'following': following,
        'type': object_type,
    }, context_instance=RequestContext(request))


@anonymous_only
def forgot_password(request):
    """Allow users to reset their password by validating email ownership."""
    if request.method == 'GET':
        return render_to_response('users/forgot_password.html', {
            'form': forms.ForgotPasswordForm(),
        }, context_instance=RequestContext(request))
    # TODO - Implement


@anonymous_only
def reset_password(request, token, username):
    """Reset users password."""
    form = forms.ResetPasswordForm(data=request.POST)
    if not form.is_valid():
        messages.add_message(request, messages.ERROR,
                             _("Our bad. Something must have gone wrong."))
        return render_to_response('users/reset_password.html', {
            'form': form,
            'token': token,
            'username': username,
        }, context_instance=RequestContext(request))
    # TODO - Implement


@anonymous_only
def confirm_registration(request, token, username):
    """Confirm a users registration."""
    profile = get_object_or_404(UserProfile, username=username)
    if profile.confirmation_code != token:
        messages.error(
            request,
           _('Hmm, that doesn\'t look like the correct confirmation code'))
        log.info('Account confirmation failed for %s' % (profile,))
        return HttpResponseRedirect(reverse('users_login'))
    profile.confirmation_code = ''
    profile.save()
    messages.success(request, 'Success! You have verified your account.')
    return HttpResponseRedirect(reverse('users_login'))


@anonymous_only
def confirm_resend(request, username):
    from django.http import HttpResponse
    return HttpResponse('TODO - Implement')
