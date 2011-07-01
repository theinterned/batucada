import logging

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _

from l10n.urlresolvers import reverse
from statuses.forms import StatusForm, ImportantStatusForm
from activity.models import Activity
from projects.models import Project
from users.decorators import login_required

from drumbeat import messages

log = logging.getLogger(__name__)


@login_required
def create(request):
    if request.method != 'POST' or 'status' not in request.POST:
        return HttpResponseRedirect(reverse('dashboard'))
    form = StatusForm(data=request.POST)
    if form.is_valid():
        status = form.save(commit=False)
        status.author = request.user.get_profile()
        status.save()
    else:
        log.debug("form error: %s" % (str(form.errors)))
        messages.error(request, _('There was an error posting '
                                  'your status update'))
    return HttpResponseRedirect(reverse('dashboard'))


@login_required
def reply(request, in_reply_to):
    """Create a status update that is a reply to an activity."""
    parent = get_object_or_404(Activity, id=in_reply_to)
    if request.method == 'POST':
        form = StatusForm(data=request.POST)
        if form.is_valid():
            status = form.save(commit=False)
            status.author = request.user.get_profile()
            status.in_reply_to = parent
            status.save()
        return HttpResponseRedirect('/')
    return render_to_response('statuses/reply.html', {
        'parent': parent,
    }, context_instance=RequestContext(request))


@login_required
def create_project_status(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method != 'POST' or 'status' not in request.POST:
        return HttpResponseRedirect(project.get_absolute_url())
    if not project.is_participating(request.user):
        return HttpResponseRedirect(project.get_absolute_url())
    if project.is_organizing(request.user):
        form = ImportantStatusForm(data=request.POST)
    else:
        form = StatusForm(data=request.POST)
    if form.is_valid():
        status = form.save(commit=False)
        status.author = request.user.get_profile()
        status.project = project
        status.save()
        log.debug("Saved status by user (%d) to study group (%d): %s" % (
        status.author.id, project.id, status))
    else:
        log.debug("form error: %s" % (str(form.errors)))
        messages.error(request, _('There was an error posting '
                                  'your status update'))
    return HttpResponseRedirect(
        reverse('projects_show', kwargs=dict(slug=project.slug)))
