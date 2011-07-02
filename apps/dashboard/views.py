import random

from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage
from django.contrib.sites.models import Site
from django.utils.translation import ugettext as _

from l10n.urlresolvers import reverse
from activity.models import Activity
from users.decorators import login_required
from users.models import UserProfile
from users.forms import CreateProfileForm
from projects.models import Project
from news.models import FeedEntry
from relationships.models import Relationship
from drumbeat import messages


def splash(request):
    """Splash page we show to users who are not authenticated."""
    project = None
    projects = Project.objects.filter(featured=True)
    if projects:
        project = random.choice(projects)
        project.followers_count = Relationship.objects.filter(
            target_project=project).count()
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
def dashboard(request, page=1):
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
    current_projects = profile.get_current_projects()
    users_following = profile.following()
    users_followers = profile.followers()
    activities = Activity.objects.dashboard(request.user.get_profile())

    paginator = Paginator(activities, 25)
    try:
        current_page = paginator.page(page)
    except EmptyPage:
        raise Http404

    show_welcome = not profile.discard_welcome
    return render_to_response('dashboard/dashboard.html', {
        'current_projects': current_projects,
        'users_following': users_following,
        'users_followers': users_followers,
        'show_welcome': show_welcome,
        'paginator': paginator,
        'page_num': page,
        'next_page': int(page) + 1,
        'prev_page': int(page) - 1,
        'num_pages': paginator.num_pages,
        'page': current_page,
        'domain': Site.objects.get_current().domain,
    }, context_instance=RequestContext(request))
