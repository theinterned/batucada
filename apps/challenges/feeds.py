from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django_push.publisher.feeds import Feed, HubAtom1Feed

from projects.models import Project
from challenges.models import Challenge, Submission


class ChallengesFeed(Feed):
    feed_type = HubAtom1Feed

    def items(self):
        return Challenge.objects.active().order_by('-created_on')

    def link(self):
        return reverse('challenges_feed')

    def item_description(self, item):
        return item.brief


class SubmissionsFeed(Feed):
    feed_type = HubAtom1Feed

    def get_object(self, request, challenge):
        return get_object_or_404(Challenge, slug=challenge)

    def items(self, challenge):
        return Submission.objects.filter(challenge=challenge).filter(
            is_published=True).order_by('-created_on')

    def link(self, challenge):
        return reverse('challenges_submissions_feed',
                       kwargs=dict(challenge=challenge.slug))


class ProjectChallengesFeed(ChallengesFeed):

    def get_object(self, request, project):
        return get_object_or_404(Project, slug=project)

    def items(self, project):
        return Challenge.objects.active().filter(project=project).order_by(
            '-created_on')
