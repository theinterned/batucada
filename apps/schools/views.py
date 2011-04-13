from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from schools.models import School


def home(request, slug):
    school = get_object_or_404(School, slug=slug)
    user = request.user
    context = {
        'school': school,
    }
    return render_to_response('schools/home.html', context,
                          context_instance=RequestContext(request))
