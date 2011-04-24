import logging

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _

from l10n.urlresolvers import reverse
from statuses.forms import StatusForm, ImportantStatusForm
from statuses.models import Status
from projects.models import Project
from users.decorators import login_required

from drumbeat import messages

log = logging.getLogger(__name__)


@login_required
def create(request):
    if request.method != 'POST' or 'status' not in request.POST:
        return HttpResponseRedirect(reverse('dashboard_index'))
    form = StatusForm(data=request.POST)
    if form.is_valid():
        status = form.save(commit=False)
        status.author = request.user.get_profile()
        status.save()
    else:
        log.debug("form error: %s" % (str(form.errors)))
        messages.error(request, _('There was an error posting '
                                  'your status update'))
    return HttpResponseRedirect(reverse('dashboard_index'))


@login_required
def create_project_status(request, project_id):
    if request.method != 'POST' or 'status' not in request.POST:
        return HttpResponseRedirect(reverse('dashboard_index'))
    project = get_object_or_404(Project, id=project_id)
    profile = request.user.get_profile()
    if profile != project.created_by and not profile.user.is_superuser \
            and not project.participants().filter(user=profile).exists():
        return HttpResponseRedirect(reverse('dashboard_index'))
    if profile == project.created_by or profile.user.is_superuser:
        form = ImportantStatusForm(data=request.POST)
    else:
        form = StatusForm(data=request.POST)
    if form.is_valid():
        status = form.save(commit=False)
        status.author = request.user.get_profile()
        status.project = project
        status.save()
        log.debug("Saved status by user (%d) to study group (%d): %s" % (
        profile.id, project.id, status))
    else:
        log.debug("form error: %s" % (str(form.errors)))
        messages.error(request, _('There was an error posting '
                                  'your status update'))
    return HttpResponseRedirect(
        reverse('projects_show', kwargs=dict(slug=project.slug)))
