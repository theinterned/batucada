import jingo

from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    """Stub View"""
    return jingo.render(request, 'dashboard.html')
