from django import http
from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404

from drumbeat import messages
from users.decorators import login_required
from projects.models import Project
from projects.decorators import participation_required

from links.models import Link


@login_required
@participation_required
def link_index_up(request, slug, counter):
   #Link goes up in the sidebar index (link.index decreases).
    project = get_object_or_404(Project, slug=slug)
    try:
        counter = int(counter)
    except ValueError:
        raise http.Http404
    organizing = project.is_organizing(request.user)
    if not organizing and project.category == Project.COURSE:
        messages.error(request, _('You can not change links order.'))
        return http.HttpResponseRedirect(project.get_absolute_url())
    links = Link.objects.filter(project__pk=project.pk).order_by('index')
    if counter < 1 or links.count() <= counter:
        raise http.Http404
    prev_link = links[counter - 1]
    link = links[counter]
    prev_link.index, link.index = link.index, prev_link.index
    link.save()
    prev_link.save()
    return http.HttpResponseRedirect(project.get_absolute_url() + '#links')


@login_required
@participation_required
def link_index_down(request, slug, counter):
    #Link goes down in the sidebar index (link.index increases).
    project = get_object_or_404(Project, slug=slug)
    try:
        counter = int(counter)
    except ValueError:
        raise http.Http404
    organizing = project.is_organizing(request.user)
    if not organizing and project.category == Project.COURSE:
        messages.error(request, _('You can not change links order.'))
        return http.HttpResponseRedirect(project.get_absolute_url())
    links = Link.objects.filter(project__pk=project.pk).order_by('index')
    if counter < 0 or links.count() - 1 <= counter:
        raise http.Http404
    next_link = links[counter + 1]
    link = links[counter]
    next_link.index, link.index = link.index, next_link.index
    link.save()
    next_link.save()
    return http.HttpResponseRedirect(project.get_absolute_url() + '#links')
