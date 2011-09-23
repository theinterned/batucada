import logging

from django import http
from django.utils.translation import ugettext as _
from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string

from django_obi.views import send_badges

from users.decorators import login_required
from drumbeat import messages
from l10n.urlresolvers import reverse

from badges import forms as badge_forms
from badges.pilot import get_badge_url
from badges.models import Badge


log = logging.getLogger(__name__)


def badge_description(request, slug):
    pilot_url = get_badge_url(slug)
    if pilot_url:
        return http.HttpResponseRedirect(pilot_url)
    else:
        raise http.Http404


def show(request, slug):
    badge = get_object_or_404(Badge, slug=slug)

    context = {
        'badge': badge,
    }
    return render_to_response('badges/badge.html', context,
        context_instance=RequestContext(request))


@login_required
def create(request):
    if request.method == 'POST':
        form = badge_forms.BadgeForm(request.POST)
        if form.is_valid():
            badge = form.save()
            badge.create()
            messages.success(request,
                _('The %s has been created.') % badge.name)
            return http.HttpResponseRedirect(reverse('badges_show', kwargs={
                'slug': badge.slug,
            }))
        else:
            msg = _("Problem creating the badge.")
            messages.error(request, msg)
    else:
        form = badge_forms.BadgeForm()
    return render_to_response('badges/badge_edit_summary.html', {
        'form': form, 'new_tab': True,
    }, context_instance=RequestContext(request))


@login_required
def badges_manage_complete(request):
    msg = render_to_string('badges/success_msg.html', dict(
        obi_url=settings.MOZBADGES['hub'], email=request.user.email))
    messages.info(request, msg)
    return http.HttpResponseRedirect(reverse('users_badges_manage'))


@login_required
def badges_manage_render_failure(request, message, status=500):
    log.error('Error sending badges to the OBI: %s' % message)
    msg = _("Something has gone wrong. Hopefully it's temporary. ")
    msg += _("Please try again in a few minutes.")
    messages.error(request, msg)
    return http.HttpResponseRedirect(reverse('users_badges_manage'))


@login_required
def badges_manage(request):
    profile = request.user.get_profile()
    badges_help_url = reverse('static_page_show', kwargs=dict(
            slug='assessments-and-badges'))
    return send_badges(request,
        template_name='badges/profile_badges_manage.html',
        send_badges_complete_view='users_badges_manage_done',
        render_failure=badges_manage_render_failure,
        extra_context=dict(profile=profile, obi_url=settings.MOZBADGES['hub'],
        badges_help_url=badges_help_url, badges_tab=True))
