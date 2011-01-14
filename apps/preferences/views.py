import logging

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _

from drumbeat import messages
from users.decorators import login_required
from preferences.models import AccountPreferences

log = logging.getLogger(__name__)


@login_required
def settings(request):
    profile = request.user.get_profile()
    if request.method == 'POST':
        for key in AccountPreferences.preferences:
            if key in request.POST and request.POST[key] == 'on':
                AccountPreferences(
                    user=profile, key=key, value=1).save()
            else:
                AccountPreferences.objects.filter(
                    user=profile, key=key).delete()
        messages.success(
            request,
            _("Thank you, your settings have been saved."))
        return HttpResponseRedirect(reverse('preferences_settings'))
    preferences = AccountPreferences.objects.filter(
        user=request.user.get_profile())
    prefs = {}
    for preference in preferences:
        log.debug("%s => %s" % (preference.key, preference.value))
        prefs[preference.key] = preference.value
    return render_to_response('preferences/settings_notifications.html', prefs,
                              context_instance=RequestContext(request))


@login_required
def delete(request):
    if request.method == 'POST':
        profile = request.user.get_profile()
        profile.user.delete()
        profile.delete()
        return HttpResponseRedirect(reverse('users_logout'))
    return render_to_response('preferences/settings_delete.html', {
    }, context_instance=RequestContext(request))
