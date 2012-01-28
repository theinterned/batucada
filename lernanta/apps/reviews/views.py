from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django import http
from django.utils.translation import ugettext as _

from pagination.views import get_pagination_context
from projects.models import Project
from users.decorators import login_required
from drumbeat import messages
from l10n.urlresolvers import reverse

from reviews.models import Review
from reviews.decorators import reviewer_required
from reviews.forms import ReviewForm


@login_required
@reviewer_required
def projects_reviews_list(request, toggled_under_review=False,
        toggled_accepted=False):
    reviews = Review.objects.values('project_id')
    accepted_reviews = Review.objects.filter(
        accepted=True).values('project_id')
    projects_pending = Project.objects.exclude(
        id__in=reviews)
    projects_under_review = Project.objects.filter(
        id__in=reviews).exclude(id__in=accepted_reviews)
    projects_accepted = Project.objects.filter(
        id__in=accepted_reviews)
    context = {
        'toggled_under_review': toggled_under_review,
        'toggled_accepted': toggled_accepted,
        'pending_page_url': reverse('projects_pending_review'),
        'under_review_page_url': reverse('projects_under_review'),
        'accepted_page_url': reverse('accepted_projects')
    }
    context.update(get_pagination_context(request, projects_pending,
        24, prefix='pending_'))
    context.update(get_pagination_context(request, projects_under_review,
        24, prefix='under_review_'))
    context.update(get_pagination_context(request, projects_accepted,
        24, prefix='accepted_'))
    return render_to_response('reviews/projects_reviews_list.html',
        context, context_instance=RequestContext(request))


def pending(request):
    return projects_reviews_list(request)


def under_review(request):
    return projects_reviews_list(request, toggled_under_review=True)


def accepted(request):
    return projects_reviews_list(request, toggled_accepted=True)


@login_required
@reviewer_required
def show_project_reviews(request, slug):
    project = get_object_or_404(Project, slug=slug)
    return render_to_response('reviews/show_project_reviews.html',
        {'project': project}, context_instance=RequestContext(request))


@login_required
@reviewer_required
def review_project(request, slug):
    project = get_object_or_404(Project, slug=slug)
    profile = request.user.get_profile()
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.project = project
            review.author = profile
            review.save()
            messages.success(request, _('Review posted!'))
            return http.HttpResponseRedirect(review.get_absolute_url())
        else:
            messages.error(request, _('Please correct errors below.'))
    else:
        form = ReviewForm()
    context = {'form': form, 'project': project}
    return render_to_response('reviews/review_project.html',
        context, context_instance=RequestContext(request))
