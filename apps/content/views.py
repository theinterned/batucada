from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from users.decorators import login_required
from drumbeat import messages
from projects.decorators import participation_required
from projects.models import Project

from content.forms import PageForm, NotListedPageForm, CommentForm
from content.models import Page


def show_page(request, slug, page_slug):
    page = get_object_or_404(Page, project__slug=slug, slug=page_slug)
    if request.user.is_authenticated():
        user = request.user.get_profile()
        is_participating = page.project.participants().filter(user__pk=user.pk).exists()
    else:
        is_participating = False
    return render_to_response('content/page.html', {
        'page': page,
        'project': page.project,
        'is_participating': is_participating,
    }, context_instance=RequestContext(request))


@login_required
@participation_required
def edit_page(request, slug, page_slug):
    page = get_object_or_404(Page, project__slug=slug, slug=page_slug)
    user = request.user.get_profile()
    if page.listed:
        form_cls = PageForm
    else:
        form_cls = NotListedPageForm
    if request.method == 'POST':
        form = form_cls(request.POST, instance=page)
        if form.is_valid():
            page = form.save(commit=False)
            # the author is the last author not the creator
            # when pages have versions in the future the creator will
            # be the author of the first version.
            page.author = user
            page.save()
            messages.success(request, _('Page updated!'))
            return HttpResponseRedirect(reverse('page_show', kwargs={
                'slug': slug,
                'page_slug': page_slug,
            }))
        else:
            messages.error(request,
                           _('There was a problem saving the page.'))
    else:
        form = form_cls(instance=page)
    return render_to_response('content/edit_page.html', {
        'form': form,
        'page': page,
        'project': page.project,
    }, context_instance=RequestContext(request))


@login_required
@participation_required
def create_page(request, slug):
    project = get_object_or_404(Project, slug=slug)
    user = request.user.get_profile()
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            page = form.save(commit=False)
            page.project = project
            page.author = user
            page.save()
            messages.success(request, _('Page created!'))
            return HttpResponseRedirect(reverse('page_show', kwargs={
                'slug': slug,
                'page_slug': page.slug,
            }))
        else:
            messages.error(request,
                           _('There was a problem creating the page.'))
    else:
        form = PageForm()
    return render_to_response('content/create_page.html', {
        'form': form,
        'project': project,
    }, context_instance=RequestContext(request))


@login_required
@participation_required
def comment_page(request, slug, page_slug):
    page = get_object_or_404(Page, project__slug=slug, slug=page_slug)
    user = request.user.get_profile()
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.page = page
            comment.author = user
            comment.save()
            messages.success(request, _('Comment posted!'))
            return HttpResponseRedirect(reverse('page_show', kwargs={
                'slug': slug,
                'page_slug': page.slug,
            }))
        else:
            messages.error(request,
                           _('There was a problem posting the comment.'))
    else:
        form = CommentForm()
    return render_to_response('content/comment_page.html', {
        'form': form,
        'project': page.project,
        'page': page,
    }, context_instance=RequestContext(request))
