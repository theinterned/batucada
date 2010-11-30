import logging

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed
from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

from activity.models import Activity
from activity.schema import object_type, verbs, object_types, DerivedType

log = logging.getLogger(__name__)


class ActivityStreamAtomFeed(Atom1Feed):
    """Tweaks to Atom feed generator to include Activity Stream data."""

    def root_attributes(self):
        attrs = super(ActivityStreamAtomFeed, self).root_attributes()
        attrs.update({
            u"xmlns:activity": u"http://activitystrea.ms/spec/1.0/",
        })
        return attrs

    def _add_object_element(self, handler, obj):
        handler.startElement(u'activity:object', {})

        for k, o in object_types.iteritems():
            if o == obj['object-type']:
                if not isinstance(o, DerivedType):
                    continue
                handler.addQuickElement(u'activity:object-type', o.parent.name)

        handler.addQuickElement(u'activity:object-type', obj['object-type'])
        handler.addQuickElement(u'title', obj['title'])
        handler.addQuickElement(u'id', obj['id'])
        handler.addQuickElement(u'link', attrs=obj['link'])
        handler.endElement(u'activity:object')

    def add_item_elements(self, handler, item):
        handler.startElement(u'content', {'type': 'html'})
        handler.characters(item['description'])
        handler.endElement(u'content')

        for key, verb in verbs.iteritems():
            if verb == item['activity']['verb']:
                if isinstance(verb, DerivedType):
                    handler.addQuickElement(u'activity:verb', verb.parent.name)
        handler.addQuickElement(u'activity:verb', item['activity']['verb'])

        self._add_object_element(handler, item['activity']['object'])
        if 'target' in item['activity']:
            self._add_object_element(handler, item['activity']['target'])

        super(ActivityStreamAtomFeed, self).add_item_elements(handler, item)


class UserActivityAtomFeed(Feed):
    """
    An Atom feed that uses the Activity Atom Extensions to express activities
    performed by a specific user.
    """
    feed_type = ActivityStreamAtomFeed

    def get_object(self, request, username):
        self.request = request
        return get_object_or_404(User, username=username)

    def title(self, obj):
        f = lambda u: u.get_full_name() in '' and u or u.get_full_name()
        return _("Activity Stream for %(username)s") % {
            'username': f(obj),
        }

    def link(self, obj):
        return obj.get_absolute_url()

    def item_author_name(self, obj):
        return u"%(username)s" % {'username': obj.actor_name, }

    def item_author_link(self, obj):
        return self.request.build_absolute_uri(
            obj.actor.profile.get_absolute_url(),
        )

    def item_link(self, obj):
        return self.request.build_absolute_uri(obj.get_absolute_url())

    def items(self, user):
        return Activity.objects.from_user(user)

    def item_description(self, item):
        template = 'activity/_activity_resource.html'
        return render_to_string(template, {
            'activity': item,
            'MEDIA_URL': settings.MEDIA_URL,
        })

    def item_pubdate(self, item):
        return item.created_on

    def item_extra_kwargs(self, item):
        obj_id = self.request.build_absolute_uri(
            item.obj.get_absolute_url(),
        )
        kwargs = {
            'activity': {
                'verb': item.verb,
                'object': {
                    'object-type': object_type(item.obj),
                    'title': str(item.object_name),
                    'id': obj_id,
                    'link': {
                        'rel': 'alternate',
                        'type': 'text/html',
                        'href': obj_id,
                    }
                }
            }
        }
        if item.target:
            target_id = self.request.build_absolute_uri(
                item.target.get_absolute_url(),
            )
            kwargs['activity']['target'] = {
                'object-type': object_type(item.target),
                'title': str(item.target_name),
                'id': target_id,
                'link': {
                    'rel': 'alternate',
                    'type': 'text/html',
                    'href': target_id,
                }
            }
        return kwargs


class UserNewsActivityAtomFeed(UserActivityAtomFeed):

    def title(self, obj):
        f = lambda u: u.get_full_name() in '' and u or u.get_full_name()
        return _("News Feed for %(username)s") % {
            'username': f(obj),
        }

    def items(self, user):
        return Activity.objects.for_user(user)


class ObjectActivityAtomFeed(UserActivityAtomFeed):

    def get_object(self, request, object_id, type_id):
        content_type = ContentType.objects.get(id=type_id)
        obj = content_type.get_object_for_this_type(id=object_id)
        self.request = request
        log.debug("get_object(): " + str(obj))
        return obj

    def title(self, obj):
        return _("Activity Feed for %(project)s") % {
            'project': str(obj),
        }

    def items(self, obj):
        items = Activity.objects.from_target(obj)
        return items
