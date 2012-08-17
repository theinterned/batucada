import logging
import datetime
import unicodecsv
import itertools

from django import http
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils import simplejson
from django.utils.translation import ugettext as _
from django.template.loader import render_to_string
from django.db.models import Q, Count, Max
from django.contrib.contenttypes.models import ContentType

# from links.tasks import UnsubscribeFromFeed
from pagination.views import get_pagination_context

from projects.models import Project
from discover import forms as project_forms
from discover.models import get_popular_tags
from discover.models import get_weighted_tags
from discover.models import get_tagged_projects
from discover.models import get_course_list
from l10n.urlresolvers import reverse
from relationships.models import Relationship
from schools.models import School
from activity.models import Activity, RemoteObject
from signups.models import Signup
from reviews.models import Review

log = logging.getLogger(__name__)


def learn(request, max_count=24):
    projects = Project.objects.filter(not_listed=False,
        deleted=False).order_by('-created_on')
    get_params = request.GET.copy()
    if not 'language' in get_params:
        language = request.session.get('search_language') or 'all'
        get_params['language'] = language
    form = project_forms.ProjectsFilterForm(get_params)
    context = {
        'schools': School.objects.all(),
        'popular_tags': get_popular_tags(),
        'form': form,
        'learn_url': reverse('discover_learn'),
        'infinite_scroll': request.GET.get('infinite_scroll', False),
    }
    if form.is_valid():
        projects = projects.filter(Q(category=Project.CHALLENGE)
            | Q(sign_up__status=Signup.MODERATED)
            | Q(sign_up__status=Signup.NON_MODERATED))
        
        featured = form.cleaned_data['featured']
        projects = get_course_list(featured, projects)
        if featured == project_forms.ProjectsFilterForm.SHOWCASE:
            context['learn_showcase'] = True
        elif featured == project_forms.ProjectsFilterForm.COMMUNITY:
            context['learn_community'] = True
        elif featured == project_forms.ProjectsFilterForm.FRESH:
            context['learn_fresh'] = True

        tag = form.cleaned_data['tag']
        if tag:
            context['learn_tag'] = tag
            projects = get_tagged_projects(tag, projects)

        language = form.cleaned_data['language']
        request.session['search_language'] = language
        if language != 'all':
            projects = projects.filter(language__startswith=language)

        reviewed = form.cleaned_data['reviewed']
        if reviewed:
            accepted_reviews = Review.objects.filter(
                accepted=True).values('project_id')
            projects = projects.filter(id__in=accepted_reviews)

    context['projects'] = projects
    context.update(get_pagination_context(request, projects, max_count))
    if request.is_ajax():
        projects_html = render_to_string('discover/_learn_projects.html',
            context, context_instance=RequestContext(request))
        projects_pagination = render_to_string('discover/_learn_pagination.html',
            context, context_instance=RequestContext(request))
        learn_header = render_to_string('discover/_learn_header.html',
            context, context_instance=RequestContext(request))
        learn_filters = render_to_string('discover/_learn_filters.html',
            context, context_instance=RequestContext(request))
        data = {
            'projects_html': projects_html,
            'projects_pagination': projects_pagination,
            'learn_header': learn_header,
            'learn_filters': learn_filters,
        }
        json = simplejson.dumps(data)
        return http.HttpResponse(json, mimetype="application/json")
    return render_to_response('discover/discover.html', context,
        context_instance=RequestContext(request))


def schools(request, school_slug, max_count=24):
    school = get_object_or_404(School, slug=school_slug)
    projects = Project.objects.filter(not_listed=False,
        deleted=False).order_by('-created_on')

    get_params = request.GET.copy()
    if not 'language' in get_params:
        language = request.session.get('search_language') or 'all'
        get_params['language'] = language
    form = project_forms.ProjectsFilterForm(get_params)

    context = {
        'schools': School.objects.all(),
        'popular_tags': get_popular_tags(),
        'form': form,
        'learn_url': reverse('discover_learn'),
        'infinite_scroll': request.GET.get('infinite_scroll', False),
        'learn_school': school,
    }

    projects = projects.filter(Q(category=Project.CHALLENGE)
        | Q(sign_up__status=Signup.MODERATED)
        | Q(sign_up__status=Signup.NON_MODERATED))
    
    projects = projects.filter(school=school)

    if form.is_valid():
        language = form.cleaned_data['language']
        request.session['search_language'] = language
        if language != 'all':
            projects = projects.filter(language__startswith=language)

    context['projects'] = projects
    context.update(get_pagination_context(request, projects, max_count))
    if request.is_ajax():
        projects_html = render_to_string('discover/_learn_projects.html',
            context, context_instance=RequestContext(request))
        projects_pagination = render_to_string('discover/_learn_pagination.html',
            context, context_instance=RequestContext(request))
        learn_header = render_to_string('discover/_learn_header.html',
            context, context_instance=RequestContext(request))
        learn_filters = render_to_string('discover/_learn_filters.html',
            context, context_instance=RequestContext(request))
        data = {
            'projects_html': projects_html,
            'projects_pagination': projects_pagination,
            'learn_header': learn_header,
            'learn_filters': learn_filters,
        }
        json = simplejson.dumps(data)
        return http.HttpResponse(json, mimetype="application/json")
    return render_to_response('discover/discover.html', context,
        context_instance=RequestContext(request))


def featured(request, feature, max_count=24):
    projects = Project.objects.filter(not_listed=False,
        deleted=False).order_by('-created_on')
    get_params = request.GET.copy()

    if not 'language' in get_params:
        language = request.session.get('search_language') or 'all'
        get_params['language'] = language

    get_params['featured'] = feature
    form = project_forms.ProjectsFilterForm(get_params)

    context = {
        'schools': School.objects.all(),
        'popular_tags': get_popular_tags(),
        'form': form,
        'learn_url': reverse('discover_learn'),
        'infinite_scroll': request.GET.get('infinite_scroll', False),
    }
    projects = projects.filter(Q(category=Project.CHALLENGE)
        | Q(sign_up__status=Signup.MODERATED)
        | Q(sign_up__status=Signup.NON_MODERATED))

    if form.is_valid():
        featured = form.cleaned_data['featured']
        projects = get_course_list(featured, projects)
        if featured == project_forms.ProjectsFilterForm.SHOWCASE:
            context['learn_showcase'] = True
        elif featured == project_forms.ProjectsFilterForm.COMMUNITY:
            context['learn_community'] = True
        elif featured == project_forms.ProjectsFilterForm.FRESH:
            context['learn_fresh'] = True

    if form.is_valid():
        language = form.cleaned_data['language']
        request.session['search_language'] = language
        if language != 'all':
            projects = projects.filter(language__startswith=language)

    context['projects'] = projects
    context.update(get_pagination_context(request, projects, max_count))
    if request.is_ajax():
        projects_html = render_to_string('discover/_learn_projects.html',
            context, context_instance=RequestContext(request))
        projects_pagination = render_to_string('discover/_learn_pagination.html',
            context, context_instance=RequestContext(request))
        learn_header = render_to_string('discover/_learn_header.html',
            context, context_instance=RequestContext(request))
        learn_filters = render_to_string('discover/_learn_filters.html',
            context, context_instance=RequestContext(request))
        data = {
            'projects_html': projects_html,
            'projects_pagination': projects_pagination,
            'learn_header': learn_header,
            'learn_filters': learn_filters,
        }
        json = simplejson.dumps(data)
        return http.HttpResponse(json, mimetype="application/json")
    return render_to_response('discover/discover.html', context,
        context_instance=RequestContext(request))   


def learn_tags(request):
    tags = get_weighted_tags()
    return render_to_response('discover/discover_tags.html', {'tags': tags},
        context_instance=RequestContext(request))


def find(request, max_count=24):
    projects = Project.objects.filter(not_listed=False,
        deleted=False).order_by('-created_on')
    get_params = request.GET.copy()
    
    if not get_params.get('search_language'):
        language = request.session.get('search_language')
        if not language:
            language = 'all'
        get_params['search_language'] = language;
 
    form = project_forms.SearchPreferenceForm(projects, get_params)

    context = {
        'schools': School.objects.all(),
        'popular_tags': get_popular_tags(),
        'form': form,
        'learn_url': reverse('projects_find'),
        'infinite_scroll': request.GET.get('infinite_scroll', False),
    }

    if form.is_valid():
        language = form.cleaned_data.get('search_language')
        request.session['search_language'] = language
        if language != 'all':
            projects = projects.filter(language__startswith=language)

        reviewed = form.cleaned_data['reviewed']
        if reviewed:
            accepted_reviews = Review.objects.filter(
                accepted=True).values('project_id')
            projects = projects.filter(id__in=accepted_reviews)

    context['projects'] = projects
    context.update(get_pagination_context(request, projects, max_count))
    return render_to_response('discover/find.html', context,
        context_instance=RequestContext(request))



