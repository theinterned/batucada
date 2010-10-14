from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from activity.models import Activity

def index(request, activity_id):
    """HTML representation of a single activity."""
    activity = get_object_or_404(Activity, id=activity_id)
    return render_to_response('activity/index.html', {
        'activity': activity
    }, context_instance=RequestContext(request))
