import logging

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _

from course_tasks.forms import TaskForm
from projects.models import Project
from users.decorators import login_required

from drumbeat import messages

log = logging.getLogger(__name__)


@login_required
def create(request):
    profile = request.user.get_profile()
    if request.method == 'POST':
        form = TaskForm(data=request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.author = profile
            task.save()
            return HttpResponseRedirect(reverse('dashboard_index'))
        else:
            log.debug("form error: %s" % (str(form.errors)))
            messages.error(request, _('There was an error posting '
                                      'your course task'))
    else:
        form = TaskForm()
    return render_to_response('course_tasks/post_task.html', {
        'form': form,
    }, context_instance=RequestContext(request))

@login_required
def create_project_task(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    profile = request.user.get_profile()
    if request.method == 'POST':
        form = TaskForm(data=request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.author = request.user.get_profile()
            task.project = project
            task.save()
            log.debug("Saved task by user (%d) to course (%d): %s" % (
                profile.id, project.id, task))
            return HttpResponseRedirect(reverse('projects_show',
                kwargs=dict(slug=project.slug)))
        else:
            log.debug("form error: %s" % (str(form.errors)))
            messages.error(request, _('There was an error posting '
                                      'your course task'))
    else:
        form = TaskForm()
        form.fields['project'].initial = project.pk
    return render_to_response('course_tasks/post_task.html', {
        'form': form,
        'project': project,
    }, context_instance=RequestContext(request))
