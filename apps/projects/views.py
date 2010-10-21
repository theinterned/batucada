import re

from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from projects.models import Project
from projects.forms import ProjectForm

def show(request, slug):
    project = get_object_or_404(Project, slug=slug)
    following = (request.user.is_authenticated() and
                 request.user.is_following(project) or False)
    return render_to_response('projects/project.html', {
        'project': project,
        'type': ContentType.objects.get_for_model(project),
        'following': following,
    }, context_instance=RequestContext(request))

def gallery(request):
    return render_to_response('projects/gallery.html', {
        'projects': Project.objects.all()
    }, context_instance=RequestContext(request))

@login_required
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
