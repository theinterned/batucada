import datetime

from django import template

from content.models import Page
from signups.models import Signup

from projects.models import Project
from projects import drupal


register = template.Library()


def sidebar(context, max_people_count=64):
    user = context['user']
    project = context['project']
    sign_up = Signup.objects.get(project=project)
    is_participating = is_following = is_organizing = False
    if user.is_authenticated():
        is_participating = project.participants().filter(user=user).exists()
        profile = user.get_profile()
        is_following = profile.is_following(project)
        is_organizing = project.organizers().filter(user=user).exists()

    tags = project.tags.exclude(slug='').order_by('name')

    organizers = project.organizers()
    organizers_count = organizers.count()
    participants = project.non_organizer_participants()
    participants_count = participants.count()
    followers = project.non_participant_followers()
    followers_count = followers.count()

    # only display a subset of the participants and followers.
    remaining = max_people_count
    sidebar_organizers = organizers[:remaining]
    sidebar_participants = []
    sidebar_followers = []
    remaining -= sidebar_organizers.count()
    if remaining > 0:
        sidebar_participants = participants[:remaining]
        remaining -= sidebar_participants.count()
    if remaining > 0:
        sidebar_followers = followers[:remaining]
        remaining -= sidebar_followers.count()

    update_count = project.activities().count()
    pending_signup_answers_count = sign_up.pending_answers().count()
    content_pages = Page.objects.filter(project__pk=project.pk,
        listed=True, deleted=False).order_by('index')
    links = project.link_set.all().order_by('index')
    school = project.accepted_school()
    imported_from = None
    if project.imported_from:
        imported_from = drupal.get_course(project.imported_from)

    can_add_task = is_organizing
    if project.category != Project.COURSE:
        can_add_task = is_participating
    can_change_order = can_add_task

    chat = '#p2pu-%s-%s' % (project.id, project.slug[:10])
    context.update({
        'participating': is_participating,
        'participants_count': participants_count,
        'following': is_following,
        'followers_count': followers_count,
        'tags': tags,
        'organizing': is_organizing,
        'organizers_count': organizers_count,
        'update_count': update_count,
        'pending_signup_answers_count': pending_signup_answers_count,
        'content_pages': content_pages,
        'links': links,
        'school': school,
        'imported_from': imported_from,
        'sign_up': sign_up,
        'sidebar_organizers': sidebar_organizers,
        'sidebar_participants': sidebar_participants,
        'sidebar_followers': sidebar_followers,
        'can_add_task': can_add_task,
        'can_change_order': can_change_order,
        'chat': chat,
    })
    return context

register.inclusion_tag('projects/sidebar.html', takes_context=True)(sidebar)


def project_list(school=None, limit=8):
    listed = Project.objects.filter(under_development=False, not_listed=False,
        archived=False)
    if school:
        featured = school.featured.filter(not_listed=False, archived=False)
    else:
        featured = listed.filter(featured=True)
    active = Project.objects.get_active(limit=limit, school=school)
    popular = Project.objects.get_popular(limit=limit, school=school)
    one_week = datetime.datetime.now() - datetime.timedelta(weeks=1)
    new = listed.filter(created_on__gte=one_week).order_by('-created_on')
    open_signup_ids = Signup.objects.exclude(
        status=Signup.CLOSED).values('project')
    open_signup = listed.filter(id__in=open_signup_ids)
    under_development = Project.objects.filter(under_development=True,
        not_listed=False, archived=False)
    archived = Project.objects.filter(not_listed=False,
        archived=True).order_by('-created_on')
    if school:
        featured = featured.filter(school=school).exclude(
            id__in=school.declined.values('id'))
        new = new.filter(school=school).exclude(
            id__in=school.declined.values('id'))
        open_signup = open_signup.filter(school=school).exclude(
            id__in=school.declined.values('id'))
        under_development = under_development.filter(school=school).exclude(
            id__in=school.declined.values('id'))
        archived = archived.filter(school=school).exclude(
            id__in=school.declined.values('id'))
    if limit:
        new = new[:limit]
        archived = archived[:limit]
        under_development = under_development[:limit]
    return {'featured': featured, 'active': active, 'popular': popular,
        'new': new, 'open_signup': open_signup,
        'under_development': under_development,
        'archived': archived, 'school': school}

register.inclusion_tag('projects/_project_list.html')(project_list)
