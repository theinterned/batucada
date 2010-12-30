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

    def author_link(self, user):
        return self._request.build_absolute_uri(user.get_absolute_url())

    def title(self, user):
        return user.name

    def subtitle(self, user):
        return _('Activity feed for %s' % (user.name,))

    def link(self, user):
        return reverse('users_profile_view',
                       kwargs={'username': user.username})

    def get_object(self, request, username):
        self._request = request
        return get_object_or_404(UserProfile, username=username)

    def items(self, user):
        return Activity.objects.filter(actor=user).order_by('-created_on')[:25]

    def item_title(self, item):
        return item.textual_representation()

    def item_description(self, item):
        return item.textual_representation()

    def item_link(self, item):
        return self._request.build_absolute_uri(item.get_absolute_url())
