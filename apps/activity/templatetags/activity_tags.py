from django import template


register = template.Library()


@register.filter
def should_hyperlink(activity):
    article_type = 'http://activitystrea.ms/schema/1.0/article'
    follow = 'http://activitystrea.ms/schema/1.0/follow'
    if activity.verb == follow and activity.target_user:
        return True
    if not activity.remote_object:
        return False
    if not activity.remote_object.uri:
        return False
    if activity.remote_object.object_type != article_type:
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
    return None


@register.filter
def should_show_verb(activity):
    note = 'http://activitystrea.ms/schema/1.0/note'
    if activity.status:
        return False
    if activity.remote_object:
        if activity.remote_object.object_type == note:
            return False
    return True


@register.filter
def friendly_verb(activity):
    if activity.verb == 'http://activitystrea.ms/schema/1.0/post':
        return 'Posted a link:'
    if activity.verb == 'http://activitystrea.ms/schema/1.0/follow':
        return 'Started following'
    return 'Unknown Verb'
