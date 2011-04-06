from django import template

from content.models import Page


register = template.Library()


def sidebar(context):
    user = context['user']
    project = context['project']
    participants = project.participants()
    is_participating = is_following = False
    if user.is_authenticated():
        is_participating = participants.filter(user__pk=user.pk).exists()
        is_following = user.get_profile().is_following(project)
    participants_count = participants.count()
    followers_count = project.non_participant_followers().count()
    update_count = project.activities().count()
    content_pages = Page.objects.filter(project__pk=project.pk, listed=True).order_by('index')
    links = project.link_set.all()
    context.update({
        'participating': is_participating,
        'participants_count': participants_count,
        'following': is_following,
        'followers_count': followers_count,
        'update_count': update_count,
        'content_pages': content_pages,
        'links': links,
    })
    return context

register.inclusion_tag('projects/sidebar.html', takes_context=True)(sidebar)


