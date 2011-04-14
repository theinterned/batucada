from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django_push.publisher.feeds import Feed, HubAtom1Feed

from projects.models import Project
from challenges.models import Challenge


class ChallengesFeed(Feed):
    feed_type = HubAtom1Feed

    def items(self):
        return Challenge.objects.active().order_by('-created_on')

    def link(self):
        return reverse('challenges_feed')

    def item_description(self, item):
        return item.brief


class ProjectChallengesFeed(ChallengesFeed):

    def get_object(self, request, project):
        return get_object_or_404(Project, slug=project)

    def items(self, project):
        return Challenge.objects.active().filter(project=project).order_by(
            '-created_on')
