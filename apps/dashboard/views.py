import jingo

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect

from users.models import Profile
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
    return jingo.render(request, 'dashboard/dashboard.html', {
        'user': request.user,
    })
       
def index(request):
    """
    Direct user to personalized dashboard or generic splash page, depending
    on whether they are logged in authenticated or not.
    """
    if request.user.is_authenticated():
        return dashboard(request)
    return splash(request)
