import logging

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from statuses.models import Status
from projects.models import Project
from users.decorators import login_required

log = logging.getLogger(__name__)


def show(request, status_id):
    status = get_object_or_404(Status, id=status_id)
    return render_to_response('statuses/show.html', {
        'status': status,
    }, context_instance=RequestContext(request))


@login_required
def create(request):
    if 'status' not in request.POST:
        return HttpResponseRedirect('/')
    status = Status(author=request.user.get_profile(),
        status=request.POST['status'])
    status.save()
    return HttpResponseRedirect('/')


@login_required
def create_project_status(request, project_id):
    if 'status' not in request.POST:
        return HttpResponseRedirect('/')
    project = get_object_or_404(Project, id=project_id)
    profile = request.user.get_profile()
    status = Status(author=profile,
                    status=request.POST['status'],
                    project=project)
    status.save()
    log.debug("Saved status by user (%d) to project (%d): %s" % (
        profile.id, project.id, status))
    return HttpResponseRedirect(
        reverse('projects_show', kwargs=dict(slug=project.slug)))
