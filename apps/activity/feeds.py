from django.contrib.auth.models import User
from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed
from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404

import jingo

from activity.models import Activity
from activity.schema import verbs, object_types, DerivedType

from l10n.urlresolvers import reverse

def object_type(obj):
    """
    Given an object, determine its type, either through inference in the case
    of models from contrib packages, or by inspecting the value of the
    ``object_type`` attribute.
    """
    inferred = {
        User: 'http://activitystrea.ms/schema/1.0/person'
    }
    for k, v in inferred.items():
        if isinstance(obj, k):
            return v
    if hasattr(obj, 'object_type'):
        attr = getattr(obj, 'object_type')
        if callable(attr):
            return attr()
        return attr
    return None

class ActivityStreamAtomFeed(Atom1Feed):
    """Tweaks to Atom feed generator to include Activity Stream data."""
    def root_attributes(self):
        attrs = super(ActivityStreamAtomFeed, self).root_attributes()
        attrs.update({
            u"xmlns:activity": u"http://activitystrea.ms/spec/1.0/",
        })
        return attrs

    def add_item_elements(self, handler, item):
        handler.startElement(u'content', {'type': 'html'})
        handler.characters(item['description'])
        handler.endElement(u'content')
        
        # if this is a specialized verb, add generalization
        for key, verb in verbs.iteritems():
            if verb == item['activity']['verb']:
                if isinstance(verb, DerivedType):
                    handler.addQuickElement(u'activity:verb', verb.parent.name)

        handler.addQuickElement(u'activity:verb', item['activity']['verb'])

        obj = item['activity']['object']
        handler.startElement(u'activity:object', {})
        
        # if this is a specialized object-type, add generalization
        for key, o in object_types.iteritems():
            if o == item['activity']['object']['object-type']:
                if isinstance(o, DerivedType):
                    handler.addQuickElement(u'activity:object-type', o.parent.name)

        handler.addQuickElement(u'activity:object-type', obj['object-type'])
        handler.addQuickElement(u'title', obj['title'])
        handler.addQuickElement(u'id', obj['id'])
        handler.addQuickElement(u'link', attrs=obj['link'])
        handler.endElement(u'activity:object')
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
            'username': f(obj)
        }
    
    def link(self, obj):
        return obj.get_absolute_url()

    def item_author_name(self, obj):
        return u"%(username)s" % { 'username': obj.actor_name }

    def item_author_link(self, obj):
        return self.request.build_absolute_uri(obj.actor.get_absolute_url())

    def item_link(self, obj):
        return self.request.build_absolute_uri(obj.get_absolute_url())
    
    def items(self, user):
        return Activity.objects.for_user(user)

    def item_description(self, item):
        template = 'activity/_activity_resource.html'
        return jingo.render_to_string(self.request, template, {
            'activity': item
        })

    def item_pubdate(self, item):
        return item.timestamp

    def item_extra_kwargs(self, item):
        obj_id = self.request.build_absolute_uri(
            item.obj.get_absolute_url()
        )
        return {
            'activity': {
                'verb': item.verb,
                'object': {
                    'object-type': object_type(item.obj),
                    'title': item.obj_name,
                    'id': obj_id,
                    'link': {
                        'rel': 'alternate',
                        'type': 'text/html',
                        'href': obj_id
                    }
                }
            }
        }

class ObjectActivityAtomFeed(Feed):
    feed_type = ActivityStreamAtomFeed
    title = "Activity Stream Example"
    link = "/foo/"
    
    def items(self):
        """Obviously a placeholder."""
        return Activity.objects.all()
