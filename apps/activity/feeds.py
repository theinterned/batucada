from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.utils.feedgenerator import Atom1Feed

from activity.models import Activity
from users.models import UserProfile


class UserActivityFeed(Feed):
    """Atom feed of user activities."""

    feed_type = Atom1Feed

    def author_name(self, user):
        return user.name

    def title(self, user):
        return user.name

    def subtitle(self, user):
        return _('Activity feed for %s' % (user.name,))

    def link(self, user):
        return reverse('users_profile_view',
                       kwargs={'username': user.username})

    def get_object(self, request, username):
        return get_object_or_404(UserProfile, username=username)

    def items(self, user):
        return Activity.objects.filter(actor=user)[:25]

    def item_title(self, item):
        return item.verb

    def item_description(self, item):
        return u"%s activity performed by %s" % (item.verb, item.actor.name)

    def item_link(self, item):
        return u'http://blah.com'
