import datetime

from django import template
from django.contrib.sites.models import Site

from content.models import Page
from signups.models import Signup
from statuses import forms as statuses_forms
from activity.views import filter_activities
from pagination.views import get_pagination_context
from activity.models import apply_filter
from l10n.urlresolvers import reverse

from projects.models import Project, PerUserTaskCompletion
from projects import drupal
from badges.models import Badge


register = template.Library()


def sidebar(context):
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
    if project.category == Project.STUDY_GROUP:
        can_add_task = is_participating
    can_change_order = can_add_task

    badges = Badge.objects.filter(groups__id=project.id)

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
        'can_add_task': can_add_task,
        'can_change_order': can_change_order,
        'chat': chat,
        'discussion_area': context.get('discussion_area', False),
        'is_challenge': (project.category == Project.CHALLENGE),
        'badges': badges
    })
    return context

register.inclusion_tag('projects/sidebar.html', takes_context=True)(sidebar)


def project_list(school=None, only_featured=False, limit=8):
    listed = Project.objects.filter(not_listed=False, archived=False)
    if school:
        featured = school.featured.filter(not_listed=False, archived=False)
    else:
        featured = listed.filter(featured=True)
    listed = listed.filter(under_development=False)
    context = {'featured': featured, 'school': school}
    if not only_featured:
        active = Project.objects.get_active(limit=limit, school=school)
        popular = Project.objects.get_popular(limit=limit, school=school)
        one_week = datetime.datetime.now() - datetime.timedelta(weeks=1)
        new_groups = listed.filter(created_on__gte=one_week).order_by('-created_on')
        open_signup_ids = Signup.objects.exclude(
            status=Signup.CLOSED).values('project')
        open_signup = listed.filter(id__in=open_signup_ids)
        under_development = Project.objects.filter(under_development=True,
            not_listed=False, archived=False)
        archived = Project.objects.filter(not_listed=False,
            archived=True).order_by('-created_on')
        if school:
            new_groups = new_groups.filter(school=school)
            open_signup = open_signup.filter(school=school)
            under_development = under_development.filter(school=school)
            archived = archived.filter(school=school)
        if limit:
            new_groups = new_groups[:limit]
            archived = archived[:limit]
            under_development = under_development[:limit]
        context.update({'active': active, 'popular': popular,
            'new_groups': new_groups, 'open_signup': open_signup,
            'under_development': under_development,
            'archived': archived})
    return context


def featured_list(school=None):
    return project_list(school, True)

register.inclusion_tag('projects/_project_list.html')(project_list)
register.inclusion_tag('projects/_project_list.html')(featured_list)


def task_list(project, user, show_all_tasks=True, short_list_length=3):
    tasks = Page.objects.filter(project=project, listed=True,
        deleted=False).order_by('index')
    tasks_count = visible_count = tasks.count()
    if not show_all_tasks:
        tasks = tasks[:short_list_length]
        visible_count = tasks.count()
    is_challenge = (project.category == Project.CHALLENGE)
    is_participating = is_organizing = False
    completed_count = 0
    if is_challenge and user.is_authenticated():
        profile = user.get_profile()
        is_organizing = project.organizers().filter(user=profile).exists()
        is_participating = project.participants().filter(user=profile).exists()
        if is_participating:
            for task in tasks:
                task.is_done = PerUserTaskCompletion.objects.filter(
                    user=profile, page=task, unchecked_on__isnull=True)
        completed_count = PerUserTaskCompletion.objects.filter(page__project=project,
            page__deleted=False, unchecked_on__isnull=True, user=profile).count()
    progressbar_value = (completed_count * 100 / tasks_count) if tasks_count else 0
    awarded_badges = project.badges.filter(badge_type=Badge.COMPLETION,
        assessment_type=Badge.SELF)
    if completed_count != tasks_count:
        awarded_badges = awarded_badges.none()
    return {
        'tasks': tasks,
        'tasks_count': tasks_count,
        'visible_count': visible_count,
        'show_all': show_all_tasks,
        'project': project,
        'is_challenge': is_challenge,
        'participating': is_participating,
        'organizing': is_organizing,
        'completed_count': completed_count,
        'progressbar_value': progressbar_value,
        'awarded_badges': awarded_badges,
    }

register.inclusion_tag('projects/_task_list.html')(task_list)


def project_wall(request, project, discussion_area=False):
    is_organizing = project.is_organizing(request.user)
    is_participating = project.is_participating(request.user)
    if is_organizing:
        form = statuses_forms.ImportantStatusForm()
    elif is_participating:
        form = statuses_forms.StatusForm()
    else:
        form = None

    activities = project.activities()
    if discussion_area:
        activities = apply_filter(activities, 'messages')
    else:
        activities = filter_activities(request, activities)

    if project.category == Project.CHALLENGE:
        url = reverse('projects_discussion_area',
            kwargs=dict(slug=project.slug))
    else:
        url = project.get_absolute_url()

    context = {
        'request': request,
        'user': request.user,
        'project': project,
        'participating': is_participating,
        'organizing': is_organizing,
        'form': form,
        'discussion_area': discussion_area,
        'domain': Site.objects.get_current().domain,
        'wall_url': url,
    }
    context.update(get_pagination_context(request, activities))
    return context

register.inclusion_tag('projects/_wall.html')(project_wall)


def project_user_list(request, project, max_count=64, with_sections=False, paginate_sections=False, user_list_url=''):
    is_challenge = (project.category == Project.CHALLENGE)
    context = {
        'request': request,
        'project': project,
        'user_list_url': user_list_url,
        'with_sections': with_sections,
        'paginate_sections': paginate_sections,
        'is_challenge': is_challenge,
    }
    if is_challenge:
        organizers = project.adopters().order_by('-organizing', '-id')
        participants = project.non_adopter_participants().order_by('-id')
        # TODO: Add section for people who completed the challenge.
        followers = project.non_participant_followers().none()
    else:
        organizers = project.organizers()
        participants = project.non_organizer_participants()
        followers = project.non_participant_followers()

    if with_sections:
        per_section_max_count = max_count / 3
        if paginate_sections:
            context.update(get_pagination_context(request, organizers, per_section_max_count,
                    prefix='organizers_'))
            context.update(get_pagination_context(request, participants, per_section_max_count,
                prefix='participants_'))
            context.update(get_pagination_context(request, followers, per_section_max_count,
                prefix='followers_'))
            context['organizers'] = context['organizers_pagination_current_page'].object_list
            context['participants'] = context['participants_pagination_current_page'].object_list
            context['followers'] = context['followers_pagination_current_page'].object_list
        else:
            context['organizers'] = organizers[:per_section_max_count]
            context['participants'] = participants[:per_section_max_count]
            context['followers'] = followers[:per_section_max_count]
            show_more_link = (organizers.count() > per_section_max_count)
            show_more_link = show_more_link or (participants.count() > per_section_max_count)
            show_more_link = show_more_link or (followers.count() > per_section_max_count)
            context['show_more_link'] = show_more_link
    else:
        remaining = max_count
        context['organizers'] = organizers[:remaining]
        remaining -= context['organizers'].count()
        if remaining > 0:
            context['participants'] = participants[:remaining]
            remaining -= context['participants'].count()
        if remaining > 0:
            context['followers'] = followers[:remaining]
            remaining -= context['followers'].count()
        # It could be equal to (remaining < 0) but the big user list page is not a
        # has more information than the sidebar section.
        context['show_more_link'] = True
    return context

register.inclusion_tag('projects/_user_list.html')(project_user_list)
