from django import template

from content.models import Page
from projects.models import Project


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
    links = project.link_set.all().order_by('index')
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


def project_list(school=None, limit=8):
    listed = Project.objects.filter(under_development=False, testing_sandbox=False)
    if school:
        featured = school.featured.filter(under_development=False, testing_sandbox=False)
    else:
        featured = listed.filter(featured=True)
    active = Project.objects.get_active(limit=limit, school=school)
    popular = Project.objects.get_popular(limit=limit, school=school)
    new = listed.order_by('-created_on')
    open_signup = listed.filter(signup_closed=False)
    under_development = Project.objects.filter(under_development=True, testing_sandbox=False)
    if school:
        featured = featured.filter(school=school)
        new = new.filter(school=school)
        open_signup = open_signup.filter(school=school)
        under_development = under_development.filter(school=school)
    if limit:
        new = new[:limit]
    return {'featured': featured, 'active': active, 'popular': popular,
           'new': new, 'open_signup': open_signup, 'under_development': under_development}

register.inclusion_tag('projects/_project_list.html')(project_list)




