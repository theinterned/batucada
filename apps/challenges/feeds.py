from django.core.urlresolvers import reverse
from django_push.publisher.feeds import Feed, HubAtom1Feed

from challenges.models import Challenge


class ChallengesFeed(Feed):
    feed_type = HubAtom1Feed

    def items(self):
        return Challenge.objects.all().order_by('-created_on')

    def link(self):
        return reverse('challenges_feed')
