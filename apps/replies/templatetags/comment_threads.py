from django import template


register = template.Library()


def comment_threads(context):
    return context

register.inclusion_tag('replies/_comment_threads.html', takes_context=True)(
    comment_threads)


def can_reply_comment(user, comment):
    return comment.page_object.can_comment(user, reply_to=comment)

register.filter('can_reply_comment', can_reply_comment)


def can_edit_comment(user, comment):
    return comment.can_edit(user)

register.filter('can_edit_comment', can_edit_comment)
