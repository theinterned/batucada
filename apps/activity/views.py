from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from activity.models import Activity


def index(request, activity_id):
    activity = get_object_or_404(Activity, id=activity_id)
    return render_to_response('activity/index.html', {
        'activity': activity,
    }, context_instance=RequestContext(request))
