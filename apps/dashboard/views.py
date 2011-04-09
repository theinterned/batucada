import random

from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db import connection
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt

from activity.models import Activity
from users.decorators import anonymous_only, login_required
from users.models import UserProfile
from users.forms import CreateProfileForm
from projects.models import Project
from dashboard.models import FeedEntry
from relationships.models import Relationship


def splash_page_activities():

    def query_list(query):
        cursor = connection.cursor()
        cursor.execute(query)
        while True:
            row = cursor.fetchone()
            if row is None:
                break
            yield row[0]

    activity_ids = query_list("""
        SELECT a.id
        FROM activity_activity a
        INNER JOIN users_userprofile u ON u.id = a.actor_id
        WHERE u.display_name IS NOT NULL
            AND u.image IS NOT NULL
            AND u.image != ''
            AND a.verb != 'http://activitystrea.ms/schema/1.0/follow'
        GROUP BY a.actor_id
        ORDER BY a.created_on DESC LIMIT 10;
    """)
    return Activity.objects.filter(
        id__in=activity_ids).order_by('-created_on')


@anonymous_only
def splash(request):
    """Splash page we show to users who are not authenticated."""
    project = None
    projects = Project.objects.filter(featured=True)
    if projects:
        project = random.choice(projects)
        project.followers_count = Relationship.objects.filter(
            target_project=project).count()
    activities = splash_page_activities()
    feed_entries = FeedEntry.objects.all().order_by('-created_on')[0:4]
    feed_url = getattr(settings, 'SPLASH_PAGE_FEED', None)
    return render_to_response('dashboard/splash.html', {
        'activities': activities,
        'featured_project': project,
        'feed_entries': feed_entries,
        'feed_url': feed_url,
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
    return HttpResponseRedirect(reverse('dashboard_index'))


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
            'display_name': ' '.join((user.first_name, user.last_name)),
            'email': user.email,
            'username': username,
        })
        return render_to_response('dashboard/setup_profile.html', {
            'form': form,
        }, context_instance=RequestContext(request))
    projects_following = profile.following(model=Project)
    for project in projects_following:
        if project.created_by == profile:
            project.relation_text = _('(organizing)')
        elif project.participants().filter(user=profile).exists():
            project.relation_text = _('(participanting)')
        else:
            project.relation_text = _('(following)')
    users_following = profile.following()
    users_followers = profile.followers()
    project_ids = [p.pk for p in projects_following]
    user_ids = [u.pk for u in users_following]
    activities = Activity.objects.select_related(
        'actor', 'status', 'project', 'remote_object',
        'remote_object__link', 'target_project').filter(
        Q(actor__exact=profile) |
        Q(actor__in=user_ids) | Q(project__in=project_ids),
    ).exclude(
        Q(verb='http://activitystrea.ms/schema/1.0/follow'),
        Q(target_user__isnull=True),
        Q(project__in=project_ids),
    ).exclude(
        Q(verb='http://activitystrea.ms/schema/1.0/follow'),
        Q(actor=profile),
    ).order_by('-created_on')[0:25]
    user_projects = Project.objects.filter(created_by=profile)
    show_welcome = not profile.discard_welcome
    return render_to_response('dashboard/dashboard.html', {
        'users_following': users_following,
        'users_followers': users_followers,
        'projects_following': projects_following,
        'activities': activities,
        'projects': user_projects,
        'show_welcome': show_welcome,
    }, context_instance=RequestContext(request))


def index(request):
    """
    Direct user to personalized dashboard or generic splash page, depending
    on whether they are logged in authenticated or not.
    """
    if request.user.is_authenticated():
        return dashboard(request)
    return splash(request)
