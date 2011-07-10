from django import template

register = template.Library()


def activity_reply_action(activity, user):
    can_reply = activity.can_reply(user)
    return {'can_reply': can_reply, 'activity': activity}

register.inclusion_tag('activity/reply_action_link.html')(
    activity_reply_action)
