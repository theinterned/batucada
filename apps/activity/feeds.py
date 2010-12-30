from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.utils.feedgenerator import Atom1Feed

from activity.models import Activity
from users.models import UserProfile


class ActivityStreamAtomFeed(Atom1Feed):

    def root_attributes(self):
        attrs = super(ActivityStreamAtomFeed, self).root_attributes()
        attrs['xmlns:activity'] = 'http://activitystrea.ms/spec/1.0/'
        return attrs

    def _add_author_info(self, handler, author_name, author_link):
        handler.startElement(u'author', {})
        handler.addQuickElement(u'activity:object-type',
                                'http://activitystrea.ms/schema/1.0/person')
        handler.addQuickElement(u'name', author_name)
        handler.addQuickElement(u'uri', author_link)
        handler.addQuickElement(u'link', u'', {
            'type': 'text/html',
            'rel': 'alternate',
            'href': author_link,
        })
        handler.endElement(u'author')

    def add_root_elements(self, handler):
        if self.feed['author_name'] is not None:
            self._add_author_info(
                handler, self.feed['author_name'], self.feed['author_link'])
        super(ActivityStreamAtomFeed, self).add_root_elements(handler)

    def add_item_elements(self, handler, item):
        if item['author_name'] is not None:
            self._add_author_info(
                handler, item['author_name'], item['author_link'])
        item['author_name'] = None
        handler.addQuickElement(u'activity:verb', item['activity']['verb'])
        obj = item['activity']['object']
        handler.startElement(u'activity:object', {})
        handler.addQuickElement(u'activity:object-type', obj['object-type'])
        handler.addQuickElement(u'link', u'', {
            'href': obj['link'],
            'rel': 'alternate',
            'type': 'text/html',
        })
        handler.addQuickElement(
            u'content', obj['content'], {'type': 'text/html'})
        handler.endElement(u'activity:object')
        super(ActivityStreamAtomFeed, self).add_item_elements(handler, item)


class UserActivityFeed(Feed):
    """Atom feed of user activities."""

    feed_type = ActivityStreamAtomFeed

    def item_author_name(self, item):
        return item.actor.name

    def item_author_link(self, item):
        return self._request.build_absolute_uri(item.actor.get_absolute_url())

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
        return item.html_representation()

    def item_link(self, item):
        return self._request.build_absolute_uri(item.get_absolute_url())

    def item_extra_kwargs(self, item):
        return {
            'activity': {
                'verb': item.verb,
                'object': {
                    'object-type': item.object_type,
                    'link': self._request.build_absolute_uri(item.object_url),
                    'content': item.html_representation(),
                },
            },
        }
