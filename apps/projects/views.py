import os
import logging

from django import http
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_http_methods

from projects import forms as project_forms
from projects.decorators import ownership_required
from projects.models import Project, ProjectMedia

from activity.models import Activity
from statuses.models import Status
from drumbeat import messages
from users.decorators import login_required

log = logging.getLogger(__name__)


def show(request, slug):
    project = get_object_or_404(Project, slug=slug)
    is_following = False
    if request.user.is_authenticated():
        profile = request.user.get_profile()
        is_following = profile.is_following(project)
    activities = Activity.objects.filter(
        Q(project=project) | Q(target_project=project),
    ).order_by('-created_on')[0:10]
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


def show_detailed(request, slug):
    project = get_object_or_404(Project, slug=slug)
    return render_to_response('projects/project_full_description.html', {
        'project': project,
    }, context_instance=RequestContext(request))


@login_required
@ownership_required
def edit(request, slug):
    project = get_object_or_404(Project, slug=slug)
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


@login_required
@ownership_required
def edit_description(request, slug):
    project = get_object_or_404(Project, slug=slug)
    if request.method == 'POST':
        form = project_forms.ProjectDescriptionForm(
            request.POST, instance=project)
        if form.is_valid():
            form.save()
            return http.HttpResponseRedirect(reverse('projects_show', kwargs={
                'slug': project.slug,
            }))
        else:
            messages.error(request,
                           _('There was a problem saving your description.'))
    else:
        form = project_forms.ProjectDescriptionForm(instance=project)
    return render_to_response('projects/project_edit_description.html', {
        'form': form,
        'project': project,
    }, context_instance=RequestContext(request))


@login_required
@ownership_required
def edit_image(request, slug):
    project = get_object_or_404(Project, slug=slug)
    if request.method == 'POST':
        form = project_forms.ProjectImageForm(request.POST, request.FILES,
                                              instance=project)
        if form.is_valid():
            messages.success(request, _('Project image updated'))
            form.save()
            return http.HttpResponseRedirect(reverse('projects_show', kwargs={
                'slug': project.slug,
            }))
        else:
            messages.error(request,
                           _('There was an error uploading your image'))
    else:
        form = project_forms.ProjectImageForm(instance=project)
    return render_to_response('projects/project_edit_image.html', {
        'project': project,
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
@ownership_required
def edit_media(request, slug):
    project = get_object_or_404(Project, slug=slug)
    files = project.projectmedia_set.all()
    if request.method == 'POST':
        if files.count() > settings.MAX_PROJECT_FILES:
            messages.error(request, _('You have already used up your allotted '
                                      'number of file uploads. Please delete '
                                      'some files and try again.'))
            return http.HttpResponseRedirect(
                reverse('projects_edit_media', kwargs=dict(slug=project.slug)))
        form = project_forms.ProjectMediaForm(request.POST, request.FILES)
        if form.is_valid():
            messages.success(request, _('File uploaded'))
            media = form.save(commit=False)
            media.project = project
            media.mime_type = form.cleaned_data['project_file'].content_type
            media.save()
            return http.HttpResponseRedirect(
                reverse('projects_edit_media', kwargs=dict(slug=project.slug)))
        else:
            messages.error(request, _('There was an error uploading '
                                      'your file.'))
    else:
        form = project_forms.ProjectMediaForm()
    files_dict = {}
    for f in files:
        files_dict[f.id] = {
            'path': os.path.basename(f.project_file.path),
            'thumbnail': f.thumbnail,
        }
    return render_to_response('projects/project_edit_media.html', {
        'files': files_dict,
        'form': form,
        'project': project,
    }, context_instance=RequestContext(request))


@login_required
@ownership_required
@require_http_methods(['POST'])
def delete_media(request, slug):
    project = get_object_or_404(Project, slug=slug)
    file_id = int(request.POST['file_id'])
    file_obj = ProjectMedia.objects.get(
        project=project, pk=file_id)
    os.unlink(file_obj.project_file.path)
    file_obj.delete()
    messages.success(request, _("The file has been deleted."))
    return http.HttpResponseRedirect(reverse('projects_edit_media', kwargs={
        'slug': project.slug,
    }))


@login_required
@ownership_required
def edit_links(request, slug):
    project = get_object_or_404(Project, slug=slug)
    if request.method == 'POST':
        form = project_forms.ProjectLinksForm(request.POST)
        if form.is_valid():
            link = form.save(commit=False)
            link.project = project
            link.user = project.created_by
            link.save()
            messages.success(request, _('Project link added.'))
            return http.HttpResponseRedirect(
                reverse('projects_edit_links', kwargs=dict(slug=project.slug)))
        else:
            messages.error(request, _('There was an error adding your link.'))
    else:
        form = project_forms.ProjectLinksForm()
    return render_to_response('projects/project_edit_links.html', {
        'project': project,
        'form': form,
    }, context_instance=RequestContext(request))


def edit_links_delete(request, slug):
    pass


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
