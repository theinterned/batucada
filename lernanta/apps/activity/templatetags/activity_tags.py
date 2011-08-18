from django import template

from l10n.urlresolvers import reverse

from activity.models import FILTERS

register = template.Library()


def activity_reply_action(activity, user):
    can_reply = activity.can_comment(user)
    kwargs = dict(page_app_label='activity',
        page_model='activity', page_pk=activity.id)
    if activity.scope_object:
        kwargs.update(dict(scope_app_label='projects',
            scope_model='project', scope_pk=activity.scope_object.id))
    reply_url = reverse('page_comment', kwargs=kwargs)
    return {'can_reply': can_reply, 'activity': activity,
        'reply_url': reply_url}

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
