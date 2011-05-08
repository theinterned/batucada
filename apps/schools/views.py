from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django import http
from django.utils import simplejson
from django.http import HttpResponseRedirect, HttpResponse

from users.decorators import login_required
from drumbeat import messages
from projects.models import Project

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
@school_organizer_required
def edit_featured(request, slug):
    school = get_object_or_404(School, slug=slug)
    if request.method == 'POST':
        form = school_forms.SchoolAddFeaturedForm(school, request.POST)
        if form.is_valid():
            project = form.cleaned_data['project']
            school.featured.add(project)
            school.save()
            messages.success(request, _('The study group is now featured for this school.'))
            return http.HttpResponseRedirect(
                reverse('schools_edit_featured', kwargs=dict(slug=school.slug)))
        else:
            messages.error(request, _("There was an error marking the study group as featured for this school."))
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
            "The study group stopped being featured for this school."))
    return http.HttpResponseRedirect(reverse('schools_edit_featured', kwargs={
        'slug': school.slug,
    }))
