from django import template

from activity.models import FILTERS

register = template.Library()


def activity_reply_action(activity, user):
    can_reply = activity.can_reply(user)
    return {'can_reply': can_reply, 'activity': activity}

register.inclusion_tag('activity/reply_action_link.html')(
    activity_reply_action)


def activity_filters(request, url):
    filters = list(FILTERS)
    filters.sort()
    if 'activities_filter' in request.GET:
        active_filter = request.GET['activities_filter']
    else:
        active_filter = 'default'
    return {
        'filters': filters,
        'active_filter': active_filter,
        'url': url,
    }

register.inclusion_tag('activity/filters.html')(
    activity_filters)
