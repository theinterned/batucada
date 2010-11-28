from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.http import HttpResponseForbidden
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, Context, Template
from django.utils.translation import ugettext as _

from projects.models import Project
from projects.forms import ProjectForm, ProjectContactUsersForm
from projects.forms import ProjectLinkForm

from activity.models import Activity
from statuses.models import Status


def show(request, slug):
    project = get_object_or_404(Project, slug=slug)
    following = (request.user.is_authenticated() and
                 request.user.is_following(project) or False)
    context = {
        'project': project,
        'type': ContentType.objects.get_for_model(project),
        'following': following,
        'admin': project.created_by == request.user,
        'followers_count': project.followers_count(),
        'activities': Activity.objects.from_target(project, limit=10),
        'update_count': Status.objects.filter(project=project).count(),
        'links': project.link_set.all(),
    }
    if not project.featured:
        return render_to_response('projects/project.html', context,
                                  context_instance=RequestContext(request))
    c = Context(context)
    t = Template(project.template)
    context.update(dict(custom_content=t.render(c)))
    return render_to_response('projects/featured.html', context,
                              context_instance=RequestContext(request))


@login_required
def edit(request, slug):
    project = get_object_or_404(Project, slug=slug)
    if request.user != project.created_by:
        return HttpResponseForbidden

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(
                reverse('projects_show', kwargs=dict(slug=project.slug)))
    else:
        form = ProjectForm(instance=project)

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
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()
            return HttpResponseRedirect(reverse('projects_show', kwargs={
                'slug': project.slug,
            }))
    else:
        form = ProjectForm()
    return render_to_response('projects/create.html', {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def contact_followers(request, slug):
    project = get_object_or_404(Project, slug=slug)
    if project.created_by != request.user:
        return HttpResponseForbidden()
    if request.method == 'POST':
        form = ProjectContactUsersForm(request.POST)
        if form.is_valid():
            form.save(sender=request.user)
            messages.add_message(request, messages.INFO,
                                 _("Message successfully sent."))
            return HttpResponseRedirect(reverse('projects_show', kwargs={
                'slug': project.slug,
            }))
    else:
        form = ProjectContactUsersForm()
        form.fields['project'].initial = project.pk
    return render_to_response('projects/contact_users.html', {
        'form': form,
        'project': project,
    }, context_instance=RequestContext(request))


def featured_css(request, slug):
    project = get_object_or_404(Project, slug=slug)
    return HttpResponse(project.css, mimetype='text/css')


def link_create(request, slug):
    project = get_object_or_404(Project, slug=slug)
    if project.created_by != request.user:
        return HttpResponseForbidden()
    form = ProjectLinkForm(initial=dict(project=project.pk))
    if request.method == 'POST':
        form = ProjectLinkForm(data=request.POST)
        if form.is_valid():
            messages.add_message(request, messages.INFO,
                                 _("Your link has been created"))
            form.save()
            return HttpResponseRedirect(reverse('projects_show', kwargs={
                'slug': project.slug,
            }))
    return render_to_response('projects/create_link.html', {
        'form': form,
        'project': project,
    }, context_instance=RequestContext(request))
