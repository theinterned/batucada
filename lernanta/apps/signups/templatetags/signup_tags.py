from django import template


register = template.Library()


def can_edit_signup_answer(user, answer):
    return answer.can_edit(user)

register.filter('can_edit_signup_answer', can_edit_signup_answer)
