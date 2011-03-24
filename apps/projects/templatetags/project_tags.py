from django import template

from relationships.models import Relationship
from statuses.models import Status
from content.models import Page


register = template.Library()


def sidebar(context):
    user = context['user']
    project = context['project']
    is_following = False
    if user.is_authenticated():
        is_following = user.get_profile().is_following(project)
    followers_count = Relationship.objects.filter(
        target_project=project).count()
    update_count = project.activities().count()
    content_pages = Page.objects.filter(project__pk=project.pk, listed=True)
    links = project.link_set.all()
    context.update({
        'following': is_following,
        'followers_count': followers_count,
        'update_count': update_count,
        'content_pages': content_pages,
        'links': links,
    })
    return context

register.inclusion_tag('projects/sidebar.html', takes_context=True)(sidebar)


