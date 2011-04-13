from django import template

from activity import schema

register = template.Library()


@register.filter
def truncate(value, arg):
    """
    Truncates a string after a given number of chars
    Argument: Number of chars to truncate after
    """
    try:
        length = int(arg)
    except ValueError:  # invalid literal for int()
        return value  # Fail silently.
    if not isinstance(value, basestring):
        value = str(value)
    if (len(value) > length):
        return value[:length] + "..."
    else:
        return value


@register.filter
def should_hyperlink(activity):
    if activity.verb == schema.verbs['follow']:
        return True
    if activity.project:
        return True
    if not activity.remote_object:
        return False
    if not activity.remote_object.uri:
        return False
    if activity.remote_object.object_type != schema.object_types['article']:
        return False
    return True


@register.filter
def get_link(activity):
    if activity.remote_object and activity.remote_object.uri:
        return activity.remote_object.uri
    if activity.target_user:
        return activity.target_user.get_absolute_url()


@register.filter
def get_link_name(activity):
    if activity.remote_object:
        return activity.remote_object.title
    if activity.target_user:
        return activity.target_user.name


@register.filter
def activity_representation(activity):
    if activity.status:
        return activity.status
    if activity.remote_object:
        if activity.remote_object.title:
            return activity.remote_object.title
    if activity.project:
        return activity.project
    return None


@register.filter
def should_show_verb(activity):
    if activity.status:
        return False
    if activity.remote_object:
        return False
    return True


@register.filter
def friendly_verb(activity):
    try:
        verb = schema.verbs_by_uri[activity.verb]
        return schema.past_tense[verb]
    except KeyError:
        return activity.verb
