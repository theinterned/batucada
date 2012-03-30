from django import template

from reviews.models import Reviewer

register = template.Library()


def project_review_action(project, user):
    can_review = False
    if user.is_authenticated():
        profile = user.get_profile()
        can_review = Reviewer.objects.filter(user=profile).exists()
    return {'can_review': can_review, 'project': project}

register.inclusion_tag('reviews/_project_review_action.html')(
    project_review_action)
