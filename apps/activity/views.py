from django.http import HttpResponse

import jingo
from activity.models import Activity

def index(request, activity_id):
    """HTML representation of a single activity."""
    try:
        activity = Activity.objects.get(id=activity_id)
        return jingo.render(request, 'activity/index.html', {
            'activity': activity
        })
    except Activity.DoesNotExist:
        return HttpResponse(status=404)
