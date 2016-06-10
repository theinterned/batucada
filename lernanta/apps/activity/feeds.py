from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from django.utils.feedgenerator import rfc3339_date
from django.contrib.sites.models import Site

from l10n.urlresolvers import reverse
from django_push.publisher.feeds import Feed, HubAtom1Feed
from activity.models import Activity
from activity.schema import object_types
from projects.models import Project
from users.models import UserProfile
from drumbeat.templatetags.truncate_chars import truncate_chars


class ActivityStreamFeedType(HubAtom1Feed):

    def root_attributes(self):
        attrs = super(ActivityStreamFeedType, self).root_attributes()
        attrs['xmlns:activity'] = 'http://activitystrea.ms/spec/1.0/'
        return attrs

    def _add_author_info(self, handler, author_name, author_link):
        handler.startElement(u'author', {})
        handler.addQuickElement(u'activity:object-type',
                                object_types['person'])
        handler.addQuickElement(u'name', author_name)
        handler.addQuickElement(u'uri', author_link)
        handler.endElement(u'author')

    def add_root_elements(self, handler):
        if self.feed['author_name'] is not None:
            self._add_author_info(
                handler, self.feed['author_name'], self.feed['author_link'])
        super(ActivityStreamFeedType, self).add_root_elements(handler)

    def add_item_elements(self, handler, item):
        handler.addQuickElement(u'updated', rfc3339_date(item['updated']))
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
        super(ActivityStreamFeedType, self).add_item_elements(handler, item)


class BaseActivityFeed(Feed):
    feed_type = ActivityStreamFeedType

    def item_author_name(self, item):
        return unicode(item.actor)

    def item_author_link(self, item):
        return self._request.build_absolute_uri(item.actor.get_absolute_url())

    def title(self, obj):
        return unicode(obj)

    def subtitle(self, obj):
        return _('Activity feed from %s') % (obj,)

    def item_title(self, item):
        return truncate_chars(item.textual_representation(), 130)

    def item_description(self, item):
        return item.html_representation()

    def item_link(self, item):
        return self._request.build_absolute_uri(item.get_absolute_url())

    def item_extra_kwargs(self, item):
        link = self._request.build_absolute_uri(
            item.target_object.get_absolute_url())
        return {
            'updated': item.created_on,
            'activity': {
                'verb': item.verb,
                'object': {
                    'object-type': item.target_object.object_type,
                    'link': link,
                    'content': item.html_representation(),
                },
            },
        }


class ProfileActivityFeed(BaseActivityFeed):

    def get_object(self, request, username):
        self._request = request
        return get_object_or_404(UserProfile, username=username)

    def link(self, user):
        return reverse('users_profile_view',
                       kwargs={'username': user.username})

    def items(self, user):
        return Activity.objects.for_user(user)[:25]


class DashboardActivityFeed(ProfileActivityFeed):

    def subtitle(self, user):
        return _('Activity feed from %s\'s dashboard') % (user,)

    def items(self, user):
        return Activity.objects.dashboard(user)[:25]


class ProjectActivityFeed(BaseActivityFeed):

    def get_object(self, request, slug):
        self._request = request
        return get_object_or_404(Project, slug=slug, deleted=False)

    def link(self, project):
        return reverse('projects_show', kwargs={'slug': project.slug})

    def items(self, project):
        return project.activities()[:25]


class PublicActivityFeed(BaseActivityFeed):

    def get_object(self, request):
        self._request = request
        return Site.objects.get_current().domain

    def items(self, obj):
        return Activity.objects.public()[:25]

    def link(self, user):
        return reverse('splash')
