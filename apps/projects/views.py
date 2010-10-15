import re

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from projects.models import Project
from projects.forms import ProjectForm


def show(request, slug):
    project = get_object_or_404(Project, slug=slug)
    return render_to_response('projects/project.html', {
        'project': project
    }, context_instance=RequestContext(request))

def gallery(request):
    return render_to_response('projects/gallery.html', {
        'projects': Project.objects.all()
    }, context_instance=RequestContext(request))

def create(request):
    form = ProjectForm()
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()
            return HttpResponseRedirect(reverse('projects_show',
                                                kwargs={'slug': project.slug}))
    return render_to_response('projects/create.html', {
        'form': form
    }, context_instance=RequestContext(request))
