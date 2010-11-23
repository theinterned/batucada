from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from statuses.models import Status


def show(request, status_id):
    status = get_object_or_404(Status, id=status_id)
    return render_to_response('statuses/show.html', {
        'status': status,
    }, context_instance=RequestContext(request))


def create(request):
    if 'status' not in request.POST:
        return HttpResponseRedirect('/')
    status = Status(author=request.user,
        status=request.POST['status'])
    status.save()
    return HttpResponseRedirect('/')


def create_project_status(request, project):
    pass
