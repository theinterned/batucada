from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from activity.models import Activity
from profiles.models import Profile
from users.forms import LoginForm

try:
    from l10n.urlresolvers import reverse
except ImportError:
    from django.core.urlresolvers import reverse

def splash(request):
    """Splash page we show to users who are not authenticated."""
    form = LoginForm()
    return render_to_response('dashboard/signin.html', {
        'form': form
    }, context_instance=RequestContext(request))

@login_required
def dashboard(request):
    """Personalized dashboard for authenticated users."""
    activities = Activity.objects.for_user(request.user, limit=5)    
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
