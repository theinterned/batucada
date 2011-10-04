import logging

from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.contrib.sites.models import Site
from django.contrib.sessions.models import Session

from l10n.urlresolvers import reverse
from drumbeat import messages
from users.decorators import login_required
from preferences import forms
from preferences.models import AccountPreferences

log = logging.getLogger(__name__)


PER_PROJECT_PREFERENCES = (
    'no_organizers_wall_updates',
    'no_organizers_content_updates',
    'no_participants_wall_updates',
    'no_participants_content_updates',
)


@login_required
def settings(request):
    profile = request.user.get_profile()
    participations = profile.participations.filter(left_on__isnull=True)
    if request.method == 'POST':
        for key in AccountPreferences.preferences:
            if key in request.POST and request.POST[key] == 'on':
                AccountPreferences.objects.filter(
                    user=profile, key=key).delete()
            else:
                AccountPreferences.objects.get_or_create(
                    user=profile, key=key, value=1)
        for participation in participations:
            for field in PER_PROJECT_PREFERENCES:
                key = '%s_%s' % (field, participation.project.slug)
                if key in request.POST and request.POST[key] == 'on':
                    setattr(participation, field, False)
                else:
                    setattr(participation, field, True)
            participation.save()
        messages.success(
            request,
            _("Thank you, your settings have been saved."))
        return HttpResponseRedirect(reverse('preferences_settings'))
    context = {
        'domain': Site.objects.get_current().domain,
        'participations': participations,
        'profile': profile,
        'settings_tab': True,
    }
    preferences = AccountPreferences.objects.filter(
        user=request.user.get_profile())
    for preference in preferences:
        context[preference.key] = preference.value
    return render_to_response('users/settings_notifications.html', context,
                              context_instance=RequestContext(request))


@login_required
def email(request):
    profile = request.user.get_profile()
    email = profile.user.email
    if request.method == "POST":
        form = forms.EmailEditForm(profile.username, request.POST,
            request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            messages.success(request, _('Email updated'))
            profile.user.email = profile.email
            profile.user.save()
            profile.save()
    else:
        form = forms.EmailEditForm(profile.username, instance=profile)

    return render_to_response('users/settings_email.html', {
        'profile': profile,
        'email': email,
        'form': form,
        'email_tab': True,
    }, context_instance=RequestContext(request))


@login_required
def password(request):
    profile = request.user.get_profile()
    if request.method == "POST":
        form = forms.PasswordEditForm(request.POST, request.FILES,
                                     instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.set_password(form.cleaned_data['password'])
            messages.success(request, _('Password updated'))
            profile.user = request.user
            profile.save()
        else:
            messages.error(request, _('There are errors in this form. Please '
                                      'correct them and resubmit.'))
    else:
        form = forms.PasswordEditForm(instance=profile)

    return render_to_response('users/settings_password.html', {
        'profile': profile,
        'form': form,
        'password_tab': True,
    }, context_instance=RequestContext(request))


@login_required
def delete(request):
    profile = request.user.get_profile()
    current_projects = profile.get_current_projects()
    pending_projects = []
    for project in current_projects['organizing']:
        if not project.archived and project.organizers().count() == 1:
            pending_projects.append(project)
    msg = _('You are the only organizer of %s active ')
    msg += _('study groups, courses, ...')
    if request.method == 'POST':
        if pending_projects:
            messages.error(request, msg % len(pending_projects))
            return HttpResponseRedirect(reverse('preferences_delete'))
        profile.deleted = True
        profile.user.is_active = False
        profile.save()
        profile.user.save()
        # logout the user.
        for s in Session.objects.all():
            if s.get_decoded().get('_auth_user_id') == profile.user.id:
                s.delete()
        return HttpResponseRedirect(reverse('users_logout'))
    return render_to_response('users/settings_delete.html',
        {'pending_projects': pending_projects, 'delete_tab': True},
        context_instance=RequestContext(request))
