from django.conf import settings
from django.contrib.sites.models import Site

from tracker.models import get_google_tracking_context


def django_conf(request):
    site = Site.objects.get_current()
    context =  {
        'settings': settings,
        'request': request,
        'site': site,
    }
    context.update(get_google_tracking_context(site))
    registration_event_key = 'send_registration_event'
    if registration_event_key in request.session:
        context[registration_event_key] = request.session[registration_event_key]
        del request.session[registration_event_key]
    return context
