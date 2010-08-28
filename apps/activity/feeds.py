from django.contrib.auth.models import User
from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed
from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404

from activity.models import Activity
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
        handler.addQuickElement(u'activity:verb', item['activity']['verb'])
        obj = item['activity']['object']
        handler.startElement(u'activity:object', {})
        handler.addQuickElement(u'activity:object-type', obj['object-type'])
        handler.endElement(u'activity:object')
        super(ActivityStreamAtomFeed, self).add_item_elements(handler, item)

    
class UserActivityAtomFeed(Feed):
    """
    An Atom feed that uses the Activity Atom Extensions to express activities
    performed by a specific user.
    """
    feed_type = ActivityStreamAtomFeed

    def get_object(self, request, username):
        return get_object_or_404(User, username=username)

    def title(self, obj):
        return _("Activities for %(username)s") % {
            'username': obj
        }
    
    def link(self, obj):
        return obj.get_absolute_url()

    def item_author_name(self, obj):
        return u"%(username)s" % { 'username': obj.actor.username }
    
    def items(self):
        return Activity.objects.all()

    def item_extra_kwargs(self, item):
        return {
            'activity': {
                'verb': item.verb,
                'object': {
                    'object-type': object_type(item.obj),
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
