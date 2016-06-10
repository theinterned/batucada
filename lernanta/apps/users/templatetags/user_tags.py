from django import template

from badges.models import get_awarded_badges
from projects import drupal as projects_drupal
from links.models import Link
from badges.models import Badge, Award

register = template.Library()


def user_sidebar(context, max_people_count=64):
    profile = context['profile']
    profile_view = context['profile_view']

    links = Link.objects.filter(user=profile,
        project__isnull=True).order_by('index')

    context.update({
        'links': links,
    })
    return context

register.inclusion_tag('users/sidebar.html', takes_context=True)(user_sidebar)


def profile_info(context):
    profile = context['profile']

    current_projects = profile.get_current_projects(only_public=True)
    users_following = profile.following()
    users_followers = profile.followers()

    interests = profile.tags.filter(category='interest').exclude(
        slug='').order_by('name')
    desired_topics = profile.tags.exclude(slug='').filter(
        category='desired_topic').order_by('name')
    skills = profile.tags.filter(category='skill').exclude(
        slug='').order_by('name')
    past_projects = profile.get_past_projects(only_public=True)
    past_drupal_courses = projects_drupal.get_past_courses(
        profile.username)
    past_involvement_count = len(past_projects) + len(past_drupal_courses)
    badges = get_awarded_badges(profile.user).values()
    badges_count = len(badges)

    context.update({
        'current_projects': current_projects,
        'users_following': users_following,
        'users_followers': users_followers,
        'skills': skills,
        'interests': interests,
        'desired_topics': desired_topics,
        'past_projects': past_projects,
        'past_drupal_courses': past_drupal_courses,
        'past_involvement_count': past_involvement_count,
        'badges': badges,
        'badges_count': badges_count,
    })
    return context

register.inclusion_tag('users/_profile_info.html', takes_context=True)(profile_info)
