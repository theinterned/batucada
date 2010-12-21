from django import http
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _

from projects import forms as project_forms
from projects.models import Project

from activity.models import Activity
from statuses.models import Status
from drumbeat import messages


def show(request, slug):
    project = get_object_or_404(Project, slug=slug)
    is_following = False
    if request.user.is_authenticated():
        profile = request.user.get_profile()
        is_following = profile.is_following(project)
    project_type = ContentType.objects.get_for_model(project)
    activities = Activity.objects.filter(
        target_id=project.id,
        target_content_type=project_type)[0:10]
    nstatuses = Status.objects.filter(project=project).count()
    links = project.link_set.all()
    context = {
        'project': project,
        'following': is_following,
        'activities': activities,
        'update_count': nstatuses,
        'links': links,
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

    return render_to_response('projects/edit.html', {
        'form': form,
        'project': project,
    }, context_instance=RequestContext(request))


def list(request):
    return render_to_response('projects/gallery.html', {
        'projects': Project.objects.all(),
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
        form = project_forms.ProjectForm()
    return render_to_response('projects/create.html', {
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
            messages.add_message(request, messages.INFO,
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


@login_required
def link_create(request, slug):
    user = request.user.get_profile()
    project = get_object_or_404(Project, slug=slug)
    if project.created_by != user:
        return http.HttpResponseForbidden()
    form = project_forms.ProjectLinkForm(initial=dict(project=project.pk))
    if request.method == 'POST':
        form = project_forms.ProjectLinkForm(data=request.POST)
        if form.is_valid():
            messages.add_message(request, messages.INFO,
                                 _("Your link has been created"))
            form.save()
            return http.HttpResponseRedirect(reverse('projects_show', kwargs={
                'slug': project.slug,
            }))
    return render_to_response('projects/create_link.html', {
        'form': form,
        'project': project,
    }, context_instance=RequestContext(request))
