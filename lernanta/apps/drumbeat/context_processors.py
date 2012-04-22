from django.conf import settings
from django.contrib.sites.models import Site

from tracker.models import get_google_tracking_context


def django_conf(request):
    context =  {
        'settings': settings,
        'request': request,
    }
    site = Site.objects.get_current()
    context.update(get_google_tracking_context(site))
    return context
