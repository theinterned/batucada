from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.utils.timesince import timesince
from django.utils.translation import ugettext as _

from activity.schema import object_type, verbs, object_types, UnknownActivityError

class ActivityManager(models.Manager):

    def __results(self, predicate, limit):
        return self.filter(**predicate).order_by('-timestamp')[:limit]

    def from_user(self, user, limit=None):
        """Return a chronological list of activities performed by ```user```."""
        return self.__results(dict(actor=user), limit)

    def from_object(self, obj, limit=None):
        """Return a chronological list of activities involving ```obj```."""
        return self.__results({
            'obj_id': obj.id,
            'obj_content_type': ContentType.objects.get_for_model(obj)
        }, limit)

    def from_target(self, target, limit=None):
        """Return a chronological list of activities performed on ```target```."""
        return self.__results({
            'target_id': target.id,
            'target_content_type': ContentType.objects.get_for_model(target)
        }, limit)

    def for_user(self, user, limit=None):
        """
        Return a chronological list of activities performed by users that
        ```user``` is following or on objects that ```user``` is interested
        in.
        """
        if not (hasattr(user, 'following') and callable(user.following)):
            return []
        ids = [u.id for u in user.following()]
        ids.append(user.id)
        return self.__results(dict(actor__in=ids), None)

    def public(self, limit=None):
        # todo - determine visibility
        return self.__results({}, limit)
    
class Activity(models.Model):
    actor = models.ForeignKey(User)
    verb = models.CharField(max_length=120)

    obj_content_type = models.ForeignKey(ContentType, related_name='object')
    obj_id = models.PositiveIntegerField()
    obj = generic.GenericForeignKey('obj_content_type', 'obj_id')

    target_content_type = models.ForeignKey(ContentType, related_name='target', null=True)
    target_id = models.PositiveIntegerField(null=True)
    target = generic.GenericForeignKey('target_content_type', 'target_id')

    timestamp = models.DateTimeField(auto_now_add=True)

    objects = ActivityManager()

    class Meta:
        verbose_name_plural = 'activities'
        ordering = ('-timestamp', 'actor')

    @property
    def verb_object(self):
        """
        Given a URI that identified a verb, return the corresponding
        ```Type``` object.
        """
        abbrev = self.verb.split('/')[-1]
        if abbrev not in verbs:
            raise UnknownActivityError("Unknown verb: %s" % (self.verb,))
        return verbs[abbrev]
    
    @property    
    def object_name(self):
        """
        Some classes of objects (e.g., ```User```) have special naming
        rules (e.g., use full name if it is not null, otherwise username).
        Apply those rules here to get a friendly name for ```self.obj```.
        """
        name = self._get_object_name(self.obj)
        if self.obj == name:
            return u"%(obj)s" % { 'obj': self.obj }
        return name

    @property
    def object_type(self):
        """
        Given an object, try to determine it's type, which will usually be
        identified by a URI.
        """
        return object_type(self.obj)
            
    @property
    def object_type_friendly(self):
        """
        If the type URI for an object can be determined, try to find the
        friendly version. For instance, http://activitystrea.ms/schema/1.0/article
        would be 'an article'.
        """
        object_type = self.object_type
        if object_type:
            for k, v in object_types.iteritems():
                if v == object_type:
                    return v.human_readable(noun=True)
        return None

    @property
    def target_name(self):
        """
        Apply special rules (if they exist) to determining the name of the
        target of this activity.
        """
        return self._get_object_name(self.target)

    @property
    def target_type(self):
        """
        Given a target, try to determine it's type, which will usually be
        identified by a URI.
        """
        return object_type(self.target)

    @property
    def target_type_friendly(self):
        """
        If the type URI for a target can be determined, try to find the
        friendly version. For instance, http://activitystrea.ms/schema/1.0/article
        would be 'an article'.
        """
        target_type = self.target_type
        if target_type:
            for k, v in object_types.iteritems():
                if v == target_type:
                    return v.human_readable(noun=True)
        return None

    @property
    def actor_name(self):
        """
        Apply special rules (if they exist) to determine the name of the
        actor of this activity.
        """
        return self._get_object_name(self.actor)

    def __unicode__(self):
        name = self._get_object_name(self.actor)
        r = u"%(name)s %(verb)s" % {
            'name': name,
            'verb': self.verb_object.past_tense,
        }
        if self.object_type:
            r += u" %(object_type)s:" % {
                'object_type': self.object_type_friendly,
            }
        r += u" %(object)s" % { 'object': self.obj }
        if self.target:
            r += u" on %s" % (self.target,)
        return r

    def _get_object_name(self, obj):
        """
        Some objects (in the Python sense, not the Activity Streams sense)
        have special rules concerning naming. Since they're only useful for
        activity streams, process them here instead of monkey patching.
        """
        if isinstance(obj, User):
            if obj.get_full_name() not in '':
                return obj.get_full_name()
        return str(obj)

    @models.permalink
    def get_absolute_url(self):
        return ('activity_index', (), {
            'activity_id': self.id
        })
    
    def timesince(self, now=None):
        """A slightly modified version of ```django.utils.timesince.timesince```."""
        t = timesince(self.timestamp, now)
        c = lambda x: x == "0 minutes" and _("less than a minute") or x
        d = lambda x: ("hours," in x or "hour," in x) and x.split(',')[0] or x
        return d(c(t)) + _(" ago")


admin.site.register(Activity)
