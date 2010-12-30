import logging

from django import http
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _

from projects import forms as project_forms
from projects.models import Project

from activity.models import Activity
from statuses.models import Status
from drumbeat import messages

log = logging.getLogger(__name__)


def show(request, slug):
    project = get_object_or_404(Project, slug=slug)
    is_following = False
    if request.user.is_authenticated():
        profile = request.user.get_profile()
        is_following = profile.is_following(project)
    activities = Activity.objects.filter(
        project=project).order_by('-created_on')[0:10]
    nstatuses = Status.objects.filter(project=project).count()
    context = {
        'project': project,
        'following': is_following,
        'activities': activities,
        'update_count': nstatuses,
        'links': [],  # temporarily removing. TODO - add back
    }
    return render_to_response('projects/project.html', context,
                          context_instance=RequestContext(request))


@login_required
def edit(request, slug):
    user = request.user.get_profile()
    project = get_object_or_404(Project, slug=slug)
    if user != project.created_by:
        return http.HttpResponseForbidden()

    if request.method == 'POST':
        form = project_forms.ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return http.HttpResponseRedirect(
                reverse('projects_show', kwargs=dict(slug=project.slug)))
    else:
        form = project_forms.ProjectForm(instance=project)

    return render_to_response('projects/project_edit_summary.html', {
        'form': form,
        'project': project,
    }, context_instance=RequestContext(request))


def list(request):
    featured = Project.objects.filter(featured=True)
    new = Project.objects.all().order_by('-created_on')[:4]
    active = Project.objects.get_popular(limit=4)
    return render_to_response('projects/gallery.html', {
        'featured': featured,
        'new': new,
        'active': active,
    }, context_instance=RequestContext(request))


@login_required
def create(request):
    user = request.user.get_profile()
    if request.method == 'POST':
        form = project_forms.ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = user
            project.save()
            return http.HttpResponseRedirect(reverse('projects_show', kwargs={
                'slug': project.slug,
            }))
        else:
            messages.error(request,
                _("There was a problem creating your project."))
    else:
        form = project_forms.ProjectForm()
    return render_to_response('projects/project_edit_summary.html', {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def contact_followers(request, slug):
    user = request.user.get_profile()
    project = get_object_or_404(Project, slug=slug)
    if project.created_by != user:
        return http.HttpResponseForbidden()
    if request.method == 'POST':
        form = project_forms.ProjectContactUsersForm(request.POST)
        if form.is_valid():
            form.save(sender=request.user)
            messages.info(request,
                          _("Message successfully sent."))
            return http.HttpResponseRedirect(reverse('projects_show', kwargs={
                'slug': project.slug,
            }))
    else:
        form = project_forms.ProjectContactUsersForm()
        form.fields['project'].initial = project.pk
    return render_to_response('projects/contact_users.html', {
        'form': form,
        'project': project,
    }, context_instance=RequestContext(request))
