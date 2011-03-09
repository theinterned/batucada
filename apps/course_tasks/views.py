import logging

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _

from course_tasks.forms import TodoForm
from course_tasks.models import Todo
from projects.models import Project
from users.decorators import login_required

from drumbeat import messages

log = logging.getLogger(__name__)


def show(request, todo_id):
    todo = get_object_or_404(Todo, id=todo_id)
    return render_to_response('todos/show.html', {
        'todo': todo,
    }, context_instance=RequestContext(request))


@login_required
def create(request):
    if request.method != 'POST' or 'todo' not in request.POST:
        return HttpResponseRedirect('/')
    form = TodoForm(data=request.POST)
    if form.is_valid():
        todo = form.save(commit=False)
        todo.author = request.user.get_profile()
        todo.save()
    else:
        log.debug("form error: %s" % (str(form.errors)))
        messages.error(request, _('There was an error posting '
                                  'your todo update'))
    return HttpResponseRedirect('/')


@login_required
def create_project_todo(request, project_id):
    if request.method != 'POST':
        return HttpResponseRedirect('/')
    project = get_object_or_404(Project, id=project_id)
    profile = request.user.get_profile()
    form = TodoForm(data=request.POST)
    if form.is_valid():
        todo = form.save(commit=False)
        todo.author = request.user.get_profile()
        todo.project = project
        todo.save()
        log.debug("Saved todo by user (%d) to project (%d): %s" % (
            profile.id, project.id, todo))
    else:
        log.debug("form error: %s" % (str(form.errors)))
        messages.error(request, _('There was an error posting '
                                  'your todo update'))
    return HttpResponseRedirect(
        reverse('projects_show', kwargs=dict(slug=project.slug)))
