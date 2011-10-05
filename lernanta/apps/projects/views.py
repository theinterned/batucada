import logging
import datetime
import unicodecsv
import itertools

from django import http
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils import simplejson
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_http_methods
from django.template.loader import render_to_string

from commonware.decorators import xframe_sameorigin

from links import tasks as links_tasks
from pagination.views import get_pagination_context

from projects import forms as project_forms
from projects.decorators import organizer_required, participation_required
from projects.decorators import can_view_metric_overview
from projects.decorators import can_view_metric_detail
from projects.decorators import restrict_project_kind
from projects.models import Project, Participation, PerUserTaskCompletion
from projects import drupal

from l10n.urlresolvers import reverse
from relationships.models import Relationship
from links.models import Link
from users.models import UserProfile
from content.models import Page
from schools.models import School
from activity.models import Activity
from activity.schema import verbs
from signups.models import Signup
from tracker import models as tracker_models

from drumbeat import messages
from users.decorators import login_required

log = logging.getLogger(__name__)


def project_list(request):
    school = None
    project_list_url = reverse('projects_gallery')
    if 'school' in request.GET:
        try:
            school = School.objects.get(slug=request.GET['school'])
        except School.DoesNotExist:
            return http.HttpResponseRedirect(project_list_url)
    return render_to_response('projects/gallery.html', {'school': school},
                              context_instance=RequestContext(request))


def list_all(request):
    school = None
    directory_url = reverse('projects_directory')
    if 'school' in request.GET:
        try:
            school = School.objects.get(slug=request.GET['school'])
        except School.DoesNotExist:
            return http.HttpResponseRedirect(directory_url)
    projects = Project.objects.filter(not_listed=False).order_by('name')
    if school:
        projects = projects.filter(school=school)
    context = {'school': school, 'directory_url': directory_url}
    context.update(get_pagination_context(request, projects, 24))
    return render_to_response('projects/directory.html', context,
        context_instance=RequestContext(request))


@login_required
def create(request):
    user = request.user.get_profile()
    if request.method == 'POST':
        form = project_forms.ProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            act = Activity(actor=user,
                verb=verbs['post'],
                scope_object=project,
                target_object=project)
            act.save()
            participation = Participation(project=project, user=user,
                organizing=True)
            participation.save()
            new_rel, created = Relationship.objects.get_or_create(source=user,
                target_project=project)
            new_rel.deleted = False
            new_rel.save()
            detailed_description_content = render_to_string(
                "projects/detailed_description_initial_content.html",
                {})
            detailed_description = Page(title=_('Full Description'),
                slug='full-description', content=detailed_description_content,
                listed=False, author_id=user.id, project_id=project.id)
            if project.category != Project.STUDY_GROUP:
                detailed_description.collaborative = False
            detailed_description.save()
            project.detailed_description_id = detailed_description.id
            sign_up = Signup(author_id=user.id, project_id=project.id)
            sign_up.save()
            project.create()
            messages.success(request,
                _('The %s has been created.') % project.kind.lower())
            return http.HttpResponseRedirect(reverse('projects_show', kwargs={
                'slug': project.slug,
            }))
        else:
            msg = _("Problem creating the study group, course, ...")
            messages.error(request, msg)
    else:
        form = project_forms.ProjectForm()
    return render_to_response('projects/project_edit_summary.html', {
        'form': form, 'new_tab': True,
    }, context_instance=RequestContext(request))


@login_required
def matching_kinds(request):
    if len(request.GET['term']) == 0:
        matching_kinds = Project.objects.values_list('kind').distinct()
    else:
        matching_kinds = Project.objects.filter(
            kind__icontains=request.GET['term']).values_list('kind').distinct()
    json = simplejson.dumps([kind[0] for kind in matching_kinds])

    return http.HttpResponse(json, mimetype="application/x-javascript")


def show(request, slug):
    project = get_object_or_404(Project, slug=slug)
    is_organizing = project.is_organizing(request.user)
    is_challenge = (project.category == Project.CHALLENGE)

    context = {
        'project': project,
        'organizing': is_organizing,
        'show_all_tasks': is_challenge,
        'is_challenge': is_challenge,
    }
    return render_to_response('projects/project.html', context,
        context_instance=RequestContext(request))


@login_required
def clone(request):
    user = request.user.get_profile()
    if request.method == 'POST':
        form = project_forms.CloneProjectForm(request.POST)
        if form.is_valid():
            base_project = form.cleaned_data['project']
            project = Project(name=base_project.name,
                category=base_project.category,
                other=base_project.other,
                other_description=base_project.other_description,
                short_description=base_project.short_description,
                long_description=base_project.long_description,
                clone_of=base_project)
            project.save()
            act = Activity(actor=user,
                verb=verbs['post'],
                scope_object=project,
                target_object=project)
            act.save()
            participation = Participation(project=project, user=user,
                organizing=True)
            participation.save()
            new_rel, created = Relationship.objects.get_or_create(source=user,
                target_project=project)
            new_rel.deleted = False
            new_rel.save()
            detailed_description = Page(title=_('Full Description'),
                slug='full-description',
                content=base_project.detailed_description.content,
                listed=False, author_id=user.id, project_id=project.id)
            detailed_description.save()
            project.detailed_description_id = detailed_description.id
            base_sign_up = base_project.sign_up.get()
            sign_up = Signup(public=base_sign_up.public,
                between_participants=base_sign_up.between_participants,
                author_id=user.id, project_id=project.id)
            sign_up.save()
            project.save()
            tasks = Page.objects.filter(project=base_project, listed=True,
                deleted=False).order_by('index')
            for task in tasks:
                new_task = Page(title=task.title, content=task.content,
                    author=user, project=project)
                new_task.save()
            links = Link.objects.filter(project=base_project).order_by('index')
            for link in links:
                new_link = Link(name=link.name, url=link.url, user=user,
                    project=project)
                new_link.save()
            project.create()
            messages.success(request,
                _('The %s has been cloned.') % project.kind.lower())
            return http.HttpResponseRedirect(reverse('projects_show', kwargs={
                'slug': project.slug,
            }))
        else:
            messages.error(request,
                _("There was a problem cloning the study group, course, ..."))
    else:
        form = project_forms.CloneProjectForm()
    return render_to_response('projects/project_clone.html', {
        'form': form, 'clone_tab': True,
    }, context_instance=RequestContext(request))


@login_required
def matching_projects(request):
    if len(request.GET['term']) == 0:
        raise http.Http404

    matching_projects = Project.objects.filter(
        slug__icontains=request.GET['term'])
    json = simplejson.dumps([project.slug for project in matching_projects])

    return http.HttpResponse(json, mimetype="application/x-javascript")


@login_required
def import_from_old_site(request):
    user = request.user.get_profile()
    if request.method == 'POST':
        form = project_forms.ImportProjectForm(request.POST)
        if form.is_valid():
            course = form.cleaned_data['course']
            project = Project(name=course['name'], kind=course['kind'],
                short_description=course['short_description'],
                long_description=course['long_description'],
                imported_from=course['slug'])
            project.save()
            act = Activity(actor=user,
                verb=verbs['post'],
                scope_object=project,
                target_object=project)
            act.save()
            participation = Participation(project=project, user=user,
                organizing=True)
            participation.save()
            new_rel, created = Relationship.objects.get_or_create(source=user,
                target_project=project)
            new_rel.deleted = False
            new_rel.save()
            if course['detailed_description']:
                detailed_description_content = course['detailed_description']
            else:
                detailed_description_content = render_to_string(
                    "projects/detailed_description_initial_content.html",
                    {})
            detailed_description = Page(title=_('Full Description'),
                slug='full-description', content=detailed_description_content,
                listed=False, author_id=user.id, project_id=project.id)
            detailed_description.save()
            project.detailed_description_id = detailed_description.id
            sign_up = Signup(between_participants=course['sign_up'],
                author_id=user.id, project_id=project.id)
            sign_up.save()
            project.save()
            for title, content in course['tasks']:
                new_task = Page(title=title, content=content, author=user,
                    project=project)
                new_task.save()
            for name, url in course['links']:
                new_link = Link(name=name, url=url, user=user, project=project)
                new_link.save()
            project.create()
            messages.success(request,
                _('The %s has been imported.') % project.kind.lower())
            return http.HttpResponseRedirect(reverse('projects_show', kwargs={
                'slug': project.slug,
            }))
        else:
            msg = _("Problem importing the study group, course, ...")
            messages.error(request, msg)
    else:
        form = project_forms.ImportProjectForm()
    return render_to_response('projects/project_import.html', {
        'form': form, 'import_tab': True},
        context_instance=RequestContext(request))


@login_required
def matching_courses(request):
    if len(request.GET['term']) == 0:
        raise http.Http404

    matching_nodes = drupal.get_matching_courses(term=request.GET['term'])
    json = simplejson.dumps(matching_nodes)

    return http.HttpResponse(json, mimetype="application/x-javascript")


@login_required
@organizer_required
def edit(request, slug):
    project = get_object_or_404(Project, slug=slug)
    is_challenge = (project.category == project.CHALLENGE)
    if request.method == 'POST':
        form = project_forms.ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request,
                _('%s updated!') % project.kind.capitalize())
            return http.HttpResponseRedirect(
                reverse('projects_edit', kwargs=dict(slug=project.slug)))
    else:
        form = project_forms.ProjectForm(instance=project)
    metric_permissions = project.get_metrics_permissions(request.user)
    return render_to_response('projects/project_edit_summary.html', {
        'form': form,
        'project': project,
        'school': project.school,
        'summary_tab': True,
        'can_view_metric_overview': metric_permissions[0],
        'is_challenge': is_challenge,
    }, context_instance=RequestContext(request))


@login_required
@xframe_sameorigin
@organizer_required
@require_http_methods(['POST'])
def edit_image_async(request, slug):
    project = get_object_or_404(Project, slug=slug)
    form = project_forms.ProjectImageForm(request.POST, request.FILES,
                                          instance=project)
    if form.is_valid():
        instance = form.save()
        return http.HttpResponse(simplejson.dumps({
            'filename': instance.image.name,
        }))
    return http.HttpResponse(simplejson.dumps({
        'error': 'There was an error uploading your image.',
    }))


@login_required
@organizer_required
def edit_image(request, slug):
    project = get_object_or_404(Project, slug=slug)
    metric_permissions = project.get_metrics_permissions(request.user)
    if request.method == 'POST':
        form = project_forms.ProjectImageForm(request.POST, request.FILES,
                                              instance=project)
        if form.is_valid():
            messages.success(request, _('Image updated'))
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
        'image_tab': True,
        'can_view_metric_overview': metric_permissions[0],
        'is_challenge': (project.category == project.CHALLENGE),
    }, context_instance=RequestContext(request))


@login_required
@organizer_required
@restrict_project_kind(Project.STUDY_GROUP, Project.COURSE)
def edit_links(request, slug):
    project = get_object_or_404(Project, slug=slug)
    metric_permissions = project.get_metrics_permissions(request.user)
    profile = request.user.get_profile()
    if request.method == 'POST':
        form = project_forms.ProjectLinksForm(request.POST)
        if form.is_valid():
            link = form.save(commit=False)
            link.project = project
            link.user = profile
            link.save()
            messages.success(request, _('Link added.'))
            return http.HttpResponseRedirect(
                reverse('projects_edit_links', kwargs=dict(slug=project.slug)))
        else:
            messages.error(request, _('There was an error adding your link.'))
    else:
        form = project_forms.ProjectLinksForm()
    links = Link.objects.select_related('subscription').filter(project=project)
    return render_to_response('projects/project_edit_links.html', {
        'project': project,
        'form': form,
        'links': links,
        'links_tab': True,
        'can_view_metric_overview': metric_permissions[0],
    }, context_instance=RequestContext(request))


@login_required
@organizer_required
@restrict_project_kind(Project.STUDY_GROUP, Project.COURSE)
def edit_links_edit(request, slug, link):
    link = get_object_or_404(Link, id=link)
    form = project_forms.ProjectLinksForm(request.POST or None, instance=link)
    profile = get_object_or_404(UserProfile, user=request.user)
    project = get_object_or_404(Project, slug=slug)
    if link.project != project:
        return http.HttpResponseForbidden(_("You can't edit this link"))
    metric_permissions = project.get_metrics_permissions(request.user)
    if form.is_valid():
        if link.subscription:
            links_tasks.UnsubscribeFromFeed.apply_async(args=(link,))
            link.subscription = None
            link.save()
        link = form.save(commit=False)
        link.user = profile
        link.project = project
        link.save()
        messages.success(request, _('Link updated.'))
        return http.HttpResponseRedirect(
            reverse('projects_edit_links', kwargs=dict(slug=project.slug)))
    else:
        form = project_forms.ProjectLinksForm(instance=link)
    return render_to_response('projects/project_edit_links_edit.html', {
        'project': project,
        'form': form,
        'link': link,
        'links_tab': True,
        'can_view_metric_overview': metric_permissions[0],
    }, context_instance=RequestContext(request))


@login_required
@organizer_required
@restrict_project_kind(Project.STUDY_GROUP, Project.COURSE)
def edit_links_delete(request, slug, link):
    if request.method == 'POST':
        project = get_object_or_404(Project, slug=slug)
        link = get_object_or_404(Link, pk=link)
        if link.project != project:
            return http.HttpResponseForbidden(_("You can't edit this link"))
        link.delete()
        messages.success(request, _('The link was deleted'))
    return http.HttpResponseRedirect(
        reverse('projects_edit_links', kwargs=dict(slug=slug)))


@login_required
@organizer_required
def edit_participants(request, slug):
    project = get_object_or_404(Project, slug=slug)
    metric_permissions = project.get_metrics_permissions(request.user)
    if request.method == 'POST':
        form = project_forms.ProjectAddParticipantForm(project, request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            organizing = form.cleaned_data['organizer']
            participation = Participation(project=project, user=user,
                organizing=organizing)
            participation.save()
            new_rel, created = Relationship.objects.get_or_create(
                source=user, target_project=project)
            new_rel.deleted = False
            new_rel.save()
            messages.success(request, _('Participant added.'))
            return http.HttpResponseRedirect(reverse(
                'projects_edit_participants',
                kwargs=dict(slug=project.slug)))
        else:
            messages.error(request,
                _('There was an error adding the participant.'))
    else:
        form = project_forms.ProjectAddParticipantForm(project)
    return render_to_response('projects/project_edit_participants.html', {
        'project': project,
        'form': form,
        'participations': project.participants().order_by('joined_on'),
        'participants_tab': True,
        'can_view_metric_overview': metric_permissions[0],
        'is_challenge': (project.category == project.CHALLENGE),
    }, context_instance=RequestContext(request))


@login_required
@organizer_required
def matching_non_participants(request, slug):
    project = get_object_or_404(Project, slug=slug)
    if len(request.GET['term']) == 0:
        raise http.Http404

    non_participants = UserProfile.objects.filter(deleted=False).exclude(
        id__in=project.participants().values('user_id'))
    matching_users = non_participants.filter(
        username__icontains=request.GET['term'])
    json = simplejson.dumps([user.username for user in matching_users])

    return http.HttpResponse(json, mimetype="application/x-javascript")


@login_required
@organizer_required
def edit_participants_make_organizer(request, slug, username):
    participation = get_object_or_404(Participation,
            project__slug=slug, user__username=username, left_on__isnull=True)
    if participation.organizing or request.method != 'POST':
        return http.HttpResponseForbidden(
            _("You can't make that person an organizer"))
    participation.organizing = True
    participation.save()
    messages.success(request, _('The participant is now an organizer.'))
    return http.HttpResponseRedirect(reverse('projects_edit_participants',
        kwargs=dict(slug=participation.project.slug)))


@login_required
@organizer_required
@restrict_project_kind(Project.STUDY_GROUP, Project.COURSE)
def edit_participants_delete(request, slug, username):
    participation = get_object_or_404(Participation,
            project__slug=slug, user__username=username, left_on__isnull=True)
    if request.method == 'POST':
        participation.left_on = datetime.datetime.now()
        participation.save()
        msg = _("The participant %s has been removed.")
        messages.success(request, msg % participation.user)
    return http.HttpResponseRedirect(reverse(
        'projects_edit_participants',
        kwargs={'slug': participation.project.slug}))


@login_required
@organizer_required
@restrict_project_kind(Project.CHALLENGE)
def edit_next_steps(request, slug):
    project = get_object_or_404(Project, slug=slug)
    metric_permissions = project.get_metrics_permissions(request.user)
    if request.method == 'POST':
        form = project_forms.ProjectAddNextProjectForm(project, request.POST)
        if form.is_valid():
            next_project = form.cleaned_data['next_project']
            project.next_projects.add(next_project)
            messages.success(request, _('Next step added.'))
            return http.HttpResponseRedirect(reverse(
                'projects_edit_next_steps',
                kwargs=dict(slug=project.slug)))
        else:
            messages.error(request,
                _('There was an error adding that next step.'))
    else:
        form = project_forms.ProjectAddNextProjectForm(project)
    return render_to_response('projects/project_edit_next_steps.html', {
        'project': project,
        'form': form,
        'next_steps': project.next_projects.all(),
        'next_steps_tab': True,
        'can_view_metric_overview': metric_permissions[0],
        'is_challenge': (project.category == project.CHALLENGE),
    }, context_instance=RequestContext(request))


@login_required
@organizer_required
@restrict_project_kind(Project.CHALLENGE)
def matching_non_next_steps(request, slug):
    project = get_object_or_404(Project, slug=slug)
    if len(request.GET['term']) == 0:
        raise http.Http404

    non_next_steps = Project.objects.exclude(
        slug=slug).exclude(
        id__in=project.next_projects.values('id'))
    matching_steps = non_next_steps.filter(
        slug__icontains=request.GET['term'])
    json = simplejson.dumps([step.slug for step in matching_steps])

    return http.HttpResponse(json, mimetype="application/x-javascript")


@login_required
@organizer_required
@restrict_project_kind(Project.CHALLENGE)
def edit_next_steps_delete(request, slug, step_slug):
    project = get_object_or_404(Project, slug=slug)
    next_project = get_object_or_404(project.next_projects,
        slug=step_slug)
    if request.method == 'POST':
        project.next_projects.remove(next_project)
        kwargs = {
            'name': next_project.name,
            'kind': next_project.kind.lower(),
        }
        msg = _("The %(name)s %(kind)s is not a next step anymore.")
        messages.success(request, msg % kwargs)
    return http.HttpResponseRedirect(reverse(
        'projects_edit_next_steps',
        kwargs={'slug': project.slug}))


@login_required
@organizer_required
def edit_status(request, slug):
    project = get_object_or_404(Project, slug=slug)
    metric_permissions = project.get_metrics_permissions(request.user)
    if request.method == 'POST':
        form = project_forms.ProjectStatusForm(
            request.POST, instance=project)
        if form.is_valid():
            form.save()
            return http.HttpResponseRedirect(reverse('projects_show', kwargs={
                'slug': project.slug,
            }))
        else:
            msg = _('There was a problem saving the %s\'s status.')
            messages.error(request, msg % project.kind.lower())
    else:
        form = project_forms.ProjectStatusForm(instance=project)
    return render_to_response('projects/project_edit_status.html', {
        'form': form,
        'project': project,
        'status_tab': True,
        'can_view_metric_overview': metric_permissions[0],
        'is_challenge': (project.category == project.CHALLENGE),
    }, context_instance=RequestContext(request))


@login_required
@can_view_metric_overview
def admin_metrics(request, slug):
    """Overview metrics for course organizers.

    We only are interested in the pages of the course and the participants.
    """
    project = get_object_or_404(Project, slug=slug)
    metric_permissions = project.get_metrics_permissions(request.user)
    participants = (participant.user for participant in project.participants())
    tracker_models.update_metrics_cache(project)
    keys = ('username', 'last_active', 'course_activity_minutes',
        'comment_count', 'task_edits_count')
    metrics = tracker_models.metrics_summary(project, participants)
    data = (dict(itertools.izip(keys, d)) for d in metrics)

    return render_to_response('projects/project_admin_metrics.html', {
            'project': project,
            'can_view_metric_overview': metric_permissions[0],
            'can_view_metric_detail': metric_permissions[1],
            'data': data,
            'metrics_tab': True,
            'is_challenge': (project.category == project.CHALLENGE),
    }, context_instance=RequestContext(request))


@login_required
@can_view_metric_detail
def export_detailed_csv(request, slug):
    """Display detailed CSV for certain users."""
    project = get_object_or_404(Project, slug=slug)
    # Preprocessing
    tracker_models.update_metrics_cache(project)
    participants = project.non_organizer_participants().order_by(
        'user__username')
    participant_profiles = (participant.user for participant in participants)
    participant_ids = participants.values('user_id')
    followers = project.non_participant_followers().order_by(
        'source__username')
    follower_profiles = (follower.source for follower in followers)
    follower_ids = followers.values('source_id')
    previous_followers = project.previous_followers()
    previous_follower_profiles = (previous.source for previous
        in previous_followers)
    previous_follower_ids = project.previous_followers().values('source_id')
    headers = ["Time on Pages", "Non-zero Length Page Views",
        "Zero-length Page Views", "Comments", "Page Edits"]
    # Create csv response
    response = http.HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; '
    response['Content-Disposition'] += 'filename=detailed_report.csv'
    writer = unicodecsv.writer(response)
    writer.writerow(["Course: " + project.name])
    writer.writerow(["Data generated: " + datetime.datetime.now().strftime(
        "%b %d, %Y")])
    writer.writerow([])
    writer.writerow([])
    # Write Total Metrics
    writer.writerow(["TOTALS"])
    writer.writerow(["Participants"] + headers)
    metrics = tracker_models.user_total_metrics(project,
        participant_profiles)
    for row in metrics:
        writer.writerow(row)
    writer.writerow([])
    writer.writerow(["Followers"] + headers)
    for row in tracker_models.user_total_metrics(project, follower_profiles):
        writer.writerow(row)
    writer.writerow([])
    writer.writerow(["Previous Followers"] + headers)
    metrics = tracker_models.user_total_metrics(project,
        previous_follower_profiles)
    for row in metrics:
        writer.writerow(row)
    writer.writerow([])
    writer.writerow(["Unauthenticated Visitors"] + headers)
    for row in tracker_models.unauth_total_metrics(project):
        writer.writerow(row + ["0"] * 2)
    writer.writerow([])
    writer.writerow([])
    # Restoring profile iterators
    participant_profiles = (participant.user for participant in participants)
    follower_profiles = (follower.source for follower in followers)
    previous_follower_profiles = (previous.source for previous
        in previous_followers)
    # Write Per Page Total Metrics
    writer.writerow(["PER PAGE TOTALS"])
    writer.writerow(["Participants", "Page Paths"] + headers[:-2])
    metrics = tracker_models.user_total_per_page_metrics(project,
        participant_ids)
    for row in metrics:
        writer.writerow(row)
    writer.writerow([])
    writer.writerow(["Followers", "Page Paths"] + headers[:-2])
    metrics = tracker_models.user_total_per_page_metrics(project, follower_ids)
    for row in metrics:
        writer.writerow(row)
    writer.writerow([])
    writer.writerow(["Previous Followers", "Page Paths"] + headers[:-2])
    metrics = tracker_models.user_total_per_page_metrics(project,
        previous_follower_ids)
    for row in metrics:
        writer.writerow(row)
    writer.writerow([])
    writer.writerow(["Unauthenticated Visitors", "Page Paths"] + headers[:-2])
    for row in tracker_models.unauth_total_per_page_metrics(project):
        writer.writerow(row)
    writer.writerow([])
    writer.writerow([])
    # Write Chronological Metrics
    writer.writerow(["CHRONOLOGICAL"])
    writer.writerow(["Participants", "Dates"] + headers)
    metrics = tracker_models.chronological_user_metrics(project,
        participant_profiles)
    for row in metrics:
        writer.writerow(row)
    writer.writerow([])
    writer.writerow(["Followers", "Dates"] + headers)
    metrics = tracker_models.chronological_user_metrics(project,
        follower_profiles)
    for row in metrics:
        writer.writerow(row)
    writer.writerow([])
    writer.writerow(["Previous Followers", "Dates"] + headers)
    metrics = tracker_models.chronological_user_metrics(project,
        previous_follower_profiles)
    for row in metrics:
        writer.writerow(row)
    writer.writerow([])
    writer.writerow(["Unauthenticated Visitors", "Dates"] + headers)
    for row in tracker_models.chronological_unauth_metrics(project):
        writer.writerow(row + ["0"] * 2)
    writer.writerow([])
    writer.writerow([])
    # Write Chronological Per Page Metrics
    writer.writerow(["CHRONOLOGICAL PER PAGE"])
    writer.writerow(["Participants", "Dates", "Page Paths"] + headers[:-2])
    metrics = tracker_models.chronological_user_per_page_metrics(
        project, participant_ids)
    for row in metrics:
        writer.writerow(row)
    writer.writerow([])
    writer.writerow(["Followers", "Dates", "Page Paths"] + headers[:-2])
    metrics = tracker_models.chronological_user_per_page_metrics(
        project, follower_ids)
    for row in metrics:
        writer.writerow(row)
    writer.writerow([])
    writer.writerow(["Previous Followers", "Dates",
        "Page Paths"] + headers[:-2])
    metrics = tracker_models.chronological_user_per_page_metrics(project,
        previous_follower_ids)
    for row in metrics:
        writer.writerow(row)
    writer.writerow([])
    writer.writerow(["Unauthenticated Visitors", "Dates",
        "Page Paths"] + headers[:-2])
    for row in tracker_models.chronological_unauth_per_page_metrics(project):
        writer.writerow(row)
    writer.writerow([])
    writer.writerow([])

    return response


@login_required
@restrict_project_kind(Project.STUDY_GROUP, Project.COURSE)
def contact_organizers(request, slug):
    project = get_object_or_404(Project, slug=slug)
    if request.method == 'POST':
        form = project_forms.ProjectContactOrganizersForm(request.POST)
        if form.is_valid():
            form.save(sender=request.user)
            messages.info(request,
                          _("Message successfully sent."))
            return http.HttpResponseRedirect(project.get_absolute_url())
    else:
        form = project_forms.ProjectContactOrganizersForm()
        form.fields['project'].initial = project.pk
    return render_to_response('projects/contact_organizers.html', {
        'form': form,
        'project': project,
    }, context_instance=RequestContext(request))


def task_list(request, slug):
    project = get_object_or_404(Project, slug=slug)
    if project.category == Project.CHALLENGE:
        return http.HttpResponseRedirect(project.get_absolute_url())
    tasks = Page.objects.filter(project__pk=project.pk, listed=True,
        deleted=False).order_by('index')
    context = {
        'project': project,
        'tasks': tasks,
    }
    return render_to_response('projects/project_task_list.html', context,
        context_instance=RequestContext(request))


def discussion_area(request, slug):
    project = get_object_or_404(Project, slug=slug)
    if project.category != Project.CHALLENGE:
        return http.HttpResponseRedirect(project.get_absolute_url())
    context = {
        'project': project,
        'discussion_area': True,
    }
    return render_to_response('projects/project_discussion_area.html', context,
        context_instance=RequestContext(request))


def user_list(request, slug):
    """Display full list of users for the project."""
    project = get_object_or_404(Project, slug=slug)
    projects_users_url = reverse('projects_user_list',
        kwargs=dict(slug=project.slug))
    context = {
        'project': project,
        'projects_users_url': projects_users_url,
        'is_challenge': (project.category == Project.CHALLENGE),
    }
    return render_to_response('projects/project_user_list.html', context,
        context_instance=RequestContext(request))


@login_required
@participation_required
@restrict_project_kind(Project.CHALLENGE)
def toggle_task_completion(request, slug, page_slug):
    page = get_object_or_404(Page, project__slug=slug, slug=page_slug,
        listed=True, deleted=False)
    profile = request.user.get_profile()
    if request.method == 'POST':
        try:
            task_completion = PerUserTaskCompletion.objects.get(
                user=profile, page=page, unchecked_on__isnull=True)
            task_completion.unchecked_on = datetime.datetime.today()
            task_completion.save()
        except PerUserTaskCompletion.DoesNotExist:
            task_completion = PerUserTaskCompletion(user=profile, page=page)
            task_completion.save()
        total_count = Page.objects.filter(project__slug=slug, listed=True,
            deleted=False).count()
        completed_count = PerUserTaskCompletion.objects.filter(
            page__project__slug=slug, page__deleted=False,
            unchecked_on__isnull=True, user=profile).count()
        progressbar_value = 0
        if total_count:
            progressbar_value = (completed_count * 100 / total_count)
        json = simplejson.dumps({
            'total_count': total_count,
            'completed_count': completed_count,
            'progressbar_value': progressbar_value})
        return http.HttpResponse(json, mimetype="application/json")
