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

from users import forms
from users.models import UserProfile
from users.decorators import anonymous_only
from projects.models import Project

from drumbeat import messages

log = logging.getLogger(__name__)


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
    messages.success(request, 'Success! You have verified your account. '
                     'You may now sign in.')
    return HttpResponseRedirect(reverse('users_login'))


@anonymous_only
def confirm_resend(request, username):
    """Resend a confirmation code."""
    profile = get_object_or_404(UserProfile, username=username)
    if profile.confirmation_code:
        path = reverse('users_confirm_registration', kwargs={
            'username': profile.username,
            'token': profile.confirmation_code,
        })
        url = request.build_absolute_uri(path)
        profile.email_confirmation_code(url)
        msg = _('A confirmation code has been sent to the email address '
                'associated with your account.')
        messages.info(request, msg)
    return HttpResponseRedirect(reverse('users_login'))


def profile_view(request, username):
    profile = get_object_or_404(UserProfile, username=username)
    following = profile.user.following(model=User)
    projects = profile.user.following(model=Project)
    followers = profile.user.followers()
    return render_to_response('users/profile.html', {
        'profile': profile,
        'following': following,
        'followers': followers,
        'projects': projects,
        'skills': profile.tags.filter(category='skill'),
        'interests': profile.tags.filter(category='interest'),
    }, context_instance=RequestContext(request))
