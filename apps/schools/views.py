from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django import http
from django.utils import simplejson
from django.http import HttpResponseRedirect, HttpResponse
from django.views.decorators.http import require_http_methods

from commonware.decorators import xframe_sameorigin

from users.decorators import login_required
from drumbeat import messages
from projects.models import Project
from users.models import UserProfile
from l10n.urlresolvers import reverse

from schools.decorators import school_organizer_required
from schools.models import School
from schools import forms as school_forms


def home(request, slug):
    school = get_object_or_404(School, slug=slug)
    user = request.user
    if user.is_authenticated():
        profile = user.get_profile()
        is_organizer = school.organizers.filter(id=profile.id).exists()
    else:
        is_organizer = False
    context = {
        'school': school,
        'is_organizer': is_organizer,
    }
    return render_to_response('schools/home.html', context,
                          context_instance=RequestContext(request))

def school_css(request, slug):
    school = get_object_or_404(School, slug=slug)
    return render_to_response('schools/school.css', {'school': school},
        context_instance=RequestContext(request), mimetype='text/css')

@login_required
@school_organizer_required
def edit(request, slug):
    school = get_object_or_404(School, slug=slug)
    if request.method == 'POST':
        form = school_forms.SchoolForm(request.POST, instance=school)
        if form.is_valid():
            form.save()
            messages.success(request, _('School updated!'))
            return http.HttpResponseRedirect(
                reverse('schools_edit', kwargs=dict(slug=school.slug)))
    else:
        form = school_forms.SchoolForm(instance=school)

    return render_to_response('schools/school_edit_summary.html', {
        'form': form,
        'school': school,
        'summary_tab': True,
    }, context_instance=RequestContext(request))


@login_required
@xframe_sameorigin
@school_organizer_required
@require_http_methods(['POST'])
def edit_image_async(request, slug):
    school = get_object_or_404(School, slug=slug)
    form = school_forms.SchoolImageForm(request.POST, request.FILES,
                                          instance=school)
    if form.is_valid():
        instance = form.save()
        return http.HttpResponse(simplejson.dumps({
            'filename': instance.image.name,
        }))
    return http.HttpResponse(simplejson.dumps({
        'error': 'There was an error uploading your image.',
    }))


@login_required
@school_organizer_required
def edit_image(request, slug):
    school = get_object_or_404(School, slug=slug)
    if request.method == 'POST':
        form = school_forms.SchoolImageForm(request.POST, request.FILES,
                                              instance=school)
        if form.is_valid():
            messages.success(request, _('Image updated'))
            form.save()
            return http.HttpResponseRedirect(reverse('school_home', kwargs={
                'slug': school.slug,
            }))
        else:
            messages.error(request,
                           _('There was an error uploading your image'))
    else:
        form = school_forms.SchoolImageForm(instance=school)
    return render_to_response('schools/school_edit_image.html', {
        'school': school,
        'form': form,
        'image_tab': True,
    }, context_instance=RequestContext(request))



@login_required
@school_organizer_required
def edit_organizers(request, slug):
    school = get_object_or_404(School, slug=slug)
    if request.method == 'POST':
        form = school_forms.ProjectAddOrganizerForm(school, request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            school.organizers.add(user)
            school.save()
            messages.success(request, _('School organizer added.'))
            return http.HttpResponseRedirect(
                reverse('schools_edit_organizers', kwargs=dict(slug=school.slug)))
        else:
            messages.error(request, _('There was an error adding the school organizer.'))
    else:
        form = school_forms.ProjectAddOrganizerForm(school)
    return render_to_response('schools/school_edit_organizers.html', {
        'school': school,
        'form': form,
        'organizers_tab': True,
    }, context_instance=RequestContext(request))


def matching_non_organizers(request, slug):
    school = get_object_or_404(School, slug=slug)
    if len(request.GET['term']) == 0:
        raise CommandException(_("Invalid request"))

    non_organizers = UserProfile.objects.exclude(id__in=school.organizers.values('user_id'))
    matching_users = non_organizers.filter(username__icontains = request.GET['term'])
    json = simplejson.dumps([user.username for user in matching_users])

    return HttpResponse(json, mimetype="application/x-javascript")



@login_required
@school_organizer_required
def edit_featured(request, slug):
    school = get_object_or_404(School, slug=slug)
    if request.method == 'POST':
        form = school_forms.SchoolAddFeaturedForm(school, request.POST)
        if form.is_valid():
            project = form.cleaned_data['project']
            school.featured.add(project)
            school.save()
            messages.success(request, _('The %s is now featured for this school.' % project.kind.lower()))
            return http.HttpResponseRedirect(
                reverse('schools_edit_featured', kwargs=dict(slug=school.slug)))
        else:
            messages.error(request, _("There was an error marking %s as featured for this school.") % slug)
    else:
        form = school_forms.SchoolAddFeaturedForm(school)
    return render_to_response('schools/school_edit_featured.html', {
        'school': school,
        'form': form,
        'featured': school.featured.all(),
        'featured_tab': True,
    }, context_instance=RequestContext(request))


def matching_non_featured(request, slug):
    school = get_object_or_404(School, slug=slug)
    if len(request.GET['term']) == 0:
        raise CommandException(_("Invalid request"))

    school_projects = Project.objects.filter(school=school)
    non_featured = school_projects.exclude(id__in=school.featured.values('id'))
    matching_projects = non_featured.filter(slug__icontains = request.GET['term'])
    json = simplejson.dumps([project.slug for project in matching_projects])

    return HttpResponse(json, mimetype="application/x-javascript")


@login_required
@school_organizer_required
def edit_featured_delete(request, slug, project_slug):
    school = get_object_or_404(School, slug=slug)
    project = get_object_or_404(Project, slug=project_slug)
    if request.method == 'POST':
        school.featured.remove(project)
        messages.success(request, _(
            "The %s stopped being featured for this school.") % project.kind.lower())
    return http.HttpResponseRedirect(reverse('schools_edit_featured', kwargs={
        'slug': school.slug,
    }))


@login_required
@school_organizer_required
def edit_declined(request, slug):
    school = get_object_or_404(School, slug=slug)
    if request.method == 'POST':
        form = school_forms.SchoolAddDeclinedForm(school, request.POST)
        if form.is_valid():
            project = form.cleaned_data['project']
            school.declined.add(project)
            school.save()
            messages.success(request, _('The %s was declined for this school.') % project.kind.lower())
            return http.HttpResponseRedirect(
                reverse('schools_edit_declined', kwargs=dict(slug=school.slug)))
        else:
            messages.error(request, _("There was an error marking %s as declined for this school.") % slug)
    else:
        form = school_forms.SchoolAddDeclinedForm(school)
    return render_to_response('schools/school_edit_declined.html', {
        'school': school,
        'form': form,
        'declined': school.declined.all(),
        'declined_tab': True,
    }, context_instance=RequestContext(request))


def matching_non_declined(request, slug):
    school = get_object_or_404(School, slug=slug)
    if len(request.GET['term']) == 0:
        raise CommandException(_("Invalid request"))

    school_projects = Project.objects.filter(school=school)
    non_declined = school_projects.exclude(id__in=school.declined.values('id'))
    matching_projects = non_declined.filter(slug__icontains = request.GET['term'])
    json = simplejson.dumps([project.slug for project in matching_projects])

    return HttpResponse(json, mimetype="application/x-javascript")


@login_required
@school_organizer_required
def edit_declined_delete(request, slug, project_slug):
    school = get_object_or_404(School, slug=slug)
    project = get_object_or_404(Project, slug=project_slug)
    if request.method == 'POST':
        school.declined.remove(project)
        messages.success(request, _(
            "The %s stopped being declined for this school.") % project.kind.lower())
    return http.HttpResponseRedirect(reverse('schools_edit_declined', kwargs={
        'slug': school.slug,
    }))

