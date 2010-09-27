from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from activity.models import Activity

def index(request, activity_id):
    """HTML representation of a single activity."""
    try:
        activity = Activity.objects.get(id=activity_id)
        
        return render_to_response('activity/index.html', {
            'activity': activity
        }, context_instance=RequestContext(request))
    except Activity.DoesNotExist:
        return HttpResponse(status=404)
