from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db.models import Q

from activity.models import Activity
from users.decorators import anonymous_only
from projects.models import Project


@anonymous_only
def splash(request):
    """Splash page we show to users who are not authenticated."""
    activities = Activity.objects.all().order_by('-created_on')[0:10]
    return render_to_response('dashboard/splash.html', {
        'activities': activities,
    }, context_instance=RequestContext(request))


@login_required
def dashboard(request):
    """Personalized dashboard for authenticated users."""
    projects = [p.id for p in request.user.following(model=Project)]
    users = [u.id for u in request.user.following(
        model=request.user.__class__)]
    activities = Activity.objects.filter(
        Q(actor_id__exact=request.user.id) |
        Q(actor_id__in=users) | Q(target_id__in=projects) |
        Q(object_id__in=projects),
    ).order_by('-created_on')
    return render_to_response('dashboard/dashboard.html', {
        'user': request.user,
        'activities': activities,
    }, context_instance=RequestContext(request))


def index(request):
    """
    Direct user to personalized dashboard or generic splash page, depending
    on whether they are logged in authenticated or not.
    """
    if request.user.is_authenticated():
        return dashboard(request)
    return splash(request)
