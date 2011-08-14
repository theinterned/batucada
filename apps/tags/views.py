from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from projects.models import Project
from schools.models import School
from tags.models import GeneralTag

from l10n.urlresolvers import reverse
from pagination.views import get_pagination_context


def list_tagged_all(request, tag_slug):
    """Display a list of non-user objects that are tagged with the tag and tag type. """
    school = None
    tag = get_object_or_404(GeneralTag, slug=tag_slug)
    directory_url = reverse('tags_tagged_list', kwargs=dict(tag_slug=tag_slug))
    if 'school' in request.GET:
        try:
            school = School.objects.get(slug=request.GET['school'])
        except School.DoesNotExist:
            return http.HttpResponseRedirect(directory_url)
    projects = Project.objects.filter(not_listed=False,
        tags__slug=tag_slug).order_by('name')
    if school:
        projects = projects.filter(school=school).exclude(
            id__in=school.declined.values('id'))
    context = {
        'tagged': projects,
        'tag': tag,
        'school': school,
        'directory_url': directory_url,
    }
    context.update(get_pagination_context(request, projects, 24))
    return render_to_response('tags/directory.html', context,
        context_instance=RequestContext(request))
