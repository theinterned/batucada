import jingo

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect

from activity.models import Activity
from profiles.models import Profile
from users.forms import LoginForm
from l10n.urlresolvers import reverse

def splash(request):
    """Splash page we show to users who are not authenticated."""
    form = LoginForm()
    return jingo.render(request, 'dashboard/signin.html', {
        'form': form
    })

@login_required
def dashboard(request):
    """Personalized dashboard for authenticated users."""
    # TODO - this is for testing, replace with activites from users
    #        and projects that the user follows.
    activities = Activity.objects.from_user(request.user, limit=5)
    activity_data = {}
    for activity in activities:
        details = activity.get_resource_details()
        activity_data[activity.id] = details
    return jingo.render(request, 'dashboard/dashboard.html', {
        'user': request.user,
        'activities': activities,
        'metadata': activity_data
    })
       
def index(request):
    """
    Direct user to personalized dashboard or generic splash page, depending
    on whether they are logged in authenticated or not.
    """
    if request.user.is_authenticated():
        return dashboard(request)
    return splash(request)
