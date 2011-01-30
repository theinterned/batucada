import logging

from django import http
from django.conf import settings
from django.contrib import auth
from django.contrib.auth import views as auth_views
from django.contrib.auth import forms as auth_forms
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson
from django.views.decorators.http import require_http_methods

from django_openid_auth import views as openid_views
from commonware.decorators import xframe_sameorigin

from users import forms
from users.models import UserProfile
from users.decorators import anonymous_only, login_required
from links.models import Link
from projects.models import Project
from drumbeat import messages
from activity.models import Activity

log = logging.getLogger(__name__)


def render_openid_failure(request, message, status, template_name):
    if request.method == 'POST':
        form = forms.OpenIDForm(request.POST)
    else:
        form = forms.OpenIDForm()
    response = render_to_string(template_name, {
        'message': message,
        'form': form,
    }, context_instance=RequestContext(request))
    return http.HttpResponse(response, status=status)


def render_openid_registration_failure(request, message, status=403):
    return render_openid_failure(
        request, message, status, 'users/register_openid.html')


def render_openid_login_failure(request, message, status=403):
    return render_openid_failure(
        request, message, status, 'users/login_openid.html')


def _clean_next_url(request):
    """Taken from zamboni. Prevent us from redirecting outside of drumbeat."""
    gets = request.GET.copy()
    url = gets['next']
    if url and '://' in url:
        url = None
    gets['next'] = url
    request.GET = gets
    return request


@anonymous_only
def login(request):
    """Log the user in. Lifted most of this code from zamboni."""

    if 'next' in request.GET:
        request = _clean_next_url(request)
        request.session['next'] = request.GET['next']

    logout(request)

    r = auth_views.login(request, template_name='users/signin.html',
                         authentication_form=forms.AuthenticationForm)

    if isinstance(r, http.HttpResponseRedirect):
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

        if request.POST.get('remember_me', None):
            request.session.set_expiry(settings.SESSION_COOKIE_AGE)
            log.debug(u'User signed in with remember_me option')

        next_param = request.session.get('next', None)
        if next_param:
            del request.session['next']
            if not next_param.startswith('/'):
                next_param = '/%s' % (next_param,)
            return http.HttpResponseRedirect(next_param)

    elif request.method == 'POST':
        messages.error(request, _('Incorrect email or password.'))
        # run through auth_views.login again to render template with messages.
        r = auth_views.login(request, template_name='users/signin.html',
                         authentication_form=forms.AuthenticationForm)

    return r


@anonymous_only
def login_openid(request):
    if request.method == 'POST':
        return openid_views.login_begin(
            request,
            template_name='users/login_openid.html',
            form_class=forms.OpenIDForm,
            login_complete_view='users_login_openid_complete')
    else:
        form = forms.OpenIDForm()
    return render_to_response('users/login_openid.html', {
        'form': form,
    }, context_instance=RequestContext(request))


@anonymous_only
def login_openid_complete(request):
    setattr(settings, 'OPENID_CREATE_USERS', False)
    return openid_views.login_complete(
        request, render_failure=render_openid_login_failure)


@login_required(profile_required=False)
def logout(request):
    """Destroy user session."""
    auth.logout(request)
    return http.HttpResponseRedirect(reverse('dashboard_index'))


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

            return http.HttpResponseRedirect(reverse('users_login'))
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
    if request.method == 'POST':
        r = openid_views.login_begin(
            request,
            template_name='users/register_openid.html',
            form_class=forms.OpenIDForm,
            login_complete_view='users_register_openid_complete')
        return r
    else:
        form = forms.OpenIDForm()
    return render_to_response('users/register_openid.html', {
        'form': form,
    }, context_instance=RequestContext(request))


@anonymous_only
def register_openid_complete(request):
    setattr(settings, 'OPENID_CREATE_USERS', True)
    return openid_views.login_complete(
        request, render_failure=render_openid_registration_failure)


def user_list(request):
    """Display a list of users on the site. Featured, new and active."""
    featured = UserProfile.objects.filter(featured=True)
    new = UserProfile.objects.all().order_by('-created_on')[:4]
    popular = UserProfile.objects.get_popular(limit=8)
    return render_to_response('users/user_list.html', {
        'featured': featured,
        'new': new,
        'popular': popular,
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
        return http.HttpResponseRedirect(reverse('users_login'))
    profile.confirmation_code = ''
    profile.save()
    messages.success(request, 'Success! You have verified your account. '
                     'You may now sign in.')
    return http.HttpResponseRedirect(reverse('users_login'))


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
    return http.HttpResponseRedirect(reverse('users_login'))


def profile_view(request, username):
    profile = get_object_or_404(UserProfile, username=username)
    following = profile.following()
    projects = profile.following(model=Project)
    followers = profile.followers()
    links = Link.objects.select_related('subscription').filter(user=profile)
    activities = Activity.objects.select_related(
        'actor', 'status', 'project').filter(
        actor=profile).order_by('-created_on')[0:25]
    return render_to_response('users/profile.html', {
        'profile': profile,
        'following': following,
        'followers': followers,
        'projects': projects,
        'skills': profile.tags.filter(category='skill'),
        'interests': profile.tags.filter(category='interest'),
        'links': links,
        'activities': activities,
    }, context_instance=RequestContext(request))


@login_required(profile_required=False)
def profile_create(request):
    if request.method != 'POST':
        return http.HttpResponseRedirect(reverse('dashboard_index'))
    try:
        request.user.get_profile()
        return http.HttpResponseRedirect(reverse('dashboard_index'))
    except UserProfile.DoesNotExist:
        pass
    form = forms.CreateProfileForm(request.POST)
    if form.is_valid():
        profile = form.save(commit=False)
        profile.user = request.user
        profile.confirmation_code = profile.generate_confirmation_code()
        profile.save()
        path = reverse('users_confirm_registration', kwargs={
            'username': profile.username,
            'token': profile.confirmation_code,
        })
        url = request.build_absolute_uri(path)
        profile.email_confirmation_code(url)
        auth.logout(request)
        msg = _('Thanks! We have sent an email to {0} with '
                'instructions for completing your '
                'registration.').format(profile.email)
        messages.info(request, msg)
        return http.HttpResponseRedirect(reverse('dashboard_index'))
    return render_to_response('dashboard/setup_profile.html', {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def profile_edit(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        form = forms.ProfileEditForm(request.POST, request.FILES,
                                     instance=profile)
        if form.is_valid():
            messages.success(request, _('Profile updated'))
            form.save()
            return http.HttpResponseRedirect(
                reverse('users_profile_view', kwargs={
                    'username': profile.username,
            }))
        else:
            messages.error(request, _('There were problems updating your '
                                      'profile. Please correct the problems '
                                      'and submit again.'))
    else:
        form = forms.ProfileEditForm(instance=profile)

#    if request.is_ajax():
#        return http.HttpResponse('profile_edit')
    return render_to_response('users/profile_edit_main.html', {
        'profile': profile,
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
@xframe_sameorigin
@require_http_methods(['POST'])
def profile_edit_image_async(request):
    log.debug("profile_edit_image_async")
    profile = get_object_or_404(UserProfile, user=request.user)
    form = forms.ProfileImageForm(request.POST, request.FILES,
                                  instance=profile)
    if form.is_valid():
        instance = form.save()
        return http.HttpResponse(simplejson.dumps({
            'filename': instance.image.name,
        }))
    return http.HttpResponse(simplejson.dumps({
        'error': 'There was an error uploading your image.',
    }))


@login_required
def profile_edit_image(request):
    profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        form = forms.ProfileImageForm(request.POST, request.FILES,
                                      instance=profile)
        if form.is_valid():
            messages.success(request, _('Profile image updated'))
            form.save()
            return http.HttpResponseRedirect(
                reverse('users_profile_edit_image'))
        else:
            messages.error(request, _('There was an error uploading '
                                      'your image.'))
    else:
        form = forms.ProfileImageForm(instance=profile)

    return render_to_response('users/profile_edit_image.html', {
        'profile': profile,
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def profile_edit_links(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        form = forms.ProfileLinksForm(request.POST)
        if form.is_valid():
            messages.success(request, _('Profile link added.'))
            link = form.save(commit=False)
            log.debug("User instance: %s" % (profile.user,))
            link.user = profile
            link.save()
            return http.HttpResponseRedirect(
                reverse('users_profile_edit_links'),
            )
        else:
            messages.error(request, _('There was an error saving '
                                      'your link.'))
    else:
        form = forms.ProfileLinksForm()
    links = Link.objects.select_related('subscription').filter(user=profile)

    return render_to_response('users/profile_edit_links.html', {
        'profile': profile,
        'form': form,
        'links': links,
    }, context_instance=RequestContext(request))


@login_required
def profile_edit_links_delete(request, link):
    if request.method == 'POST':
        profile = get_object_or_404(UserProfile, user=request.user)
        link = get_object_or_404(Link, pk=link)
        if link.user != profile:
            return http.HttpResponseForbidden()
        link.delete()
        messages.success(request, _('The link was deleted.'))
    return http.HttpResponseRedirect(reverse('users_profile_edit_links'))


def check_username(request):
    username = request.GET.get('username', None)
    if not username:
        return http.HttpResponse(status=404)
    try:
        UserProfile.objects.get(username=username)
        return http.HttpResponse()
    except UserProfile.DoesNotExist:
        return http.HttpResponse(status=404)
