import random

from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.sites.models import Site
from django.utils.translation import ugettext as _

from l10n.urlresolvers import reverse
from activity.models import Activity
from users.decorators import login_required
from users.models import UserProfile
from users.forms import CreateProfileForm
from projects.models import Project
from news.models import FeedEntry
from drumbeat import messages
from schools.models import School
from activity.views import filter_activities
from pagination.views import get_pagination_context


def splash(request):
    """Splash page we show to users who are not authenticated."""
    project = None
    projects = list(Project.objects.filter(featured=True))
    for school in School.objects.all():
        projects.extend(list(school.featured.all()))
    if projects:
        project = random.choice(projects)
    activities = Activity.objects.public()
    feed_entries = FeedEntry.objects.filter(
        page='splash').order_by('-created_on')[0:4]
    feed_url = settings.FEED_URLS['splash']
    return render_to_response('dashboard/splash.html', {
        'activities': activities,
        'featured_project': project,
        'feed_entries': feed_entries,
        'feed_url': feed_url,
        'domain': Site.objects.get_current().domain,
    }, context_instance=RequestContext(request))


@login_required
@csrf_exempt
def hide_welcome(request):
    profile = request.user.get_profile()
    if not profile.discard_welcome:
        profile.discard_welcome = True
        profile.save()
    if request.is_ajax():
        return HttpResponse()
    return HttpResponseRedirect(reverse('dashboard'))


@login_required(profile_required=False)
def dashboard(request):
    """Personalized dashboard for authenticated users."""
    try:
        profile = request.user.get_profile()
    except UserProfile.DoesNotExist:
        user = request.user
        username = ''
        if user.username[:10] != 'openiduser':
            username = user.username
        form = CreateProfileForm(initial={
            'full_name': ' '.join((user.first_name, user.last_name)),
            'email': user.email,
            'username': username,
        })
        messages.info(request,
            _('Please fill out your profile to finish registration.'))
        return render_to_response('dashboard/setup_profile.html', {
            'form': form,
        }, context_instance=RequestContext(request))
    show_welcome = not profile.discard_welcome
    activities = Activity.objects.dashboard(
        request.user.get_profile())
    activities = filter_activities(request, activities)
    context = {
        'profile': profile,
        'profile_view': False,
        'show_welcome': show_welcome,
        'domain': Site.objects.get_current().domain,
        'dashboard_url': reverse('dashboard'),
    }
    context.update(get_pagination_context(request, activities))
    return render_to_response('dashboard/dashboard.html', context,
        context_instance=RequestContext(request))
