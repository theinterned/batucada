from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.utils.timesince import timesince
from django.utils.translation import ugettext as _

from l10n.urlresolvers import reverse

import activity

class ActivityManager(models.Manager):

    def __results(self, predicate, limit):
        return self.filter(**predicate).order_by('-timestamp')[:limit]

    def from_user(self, user, limit=None):
        """Return a chronological list of activities performed by ```user```."""
        return self.__results(dict(actor=user), limit)

    def from_object(self, obj, limit=None):
        """Return a chronological list of activities involving ```obj```."""
        return self.__results(dict(obj=obj), limit)

    def from_target(self, target, limit=None):
        """Return a chronological list of activities performed on ```target```."""
        return self.__results(dict(target=target), limit)
    
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

    @property
    def readable_verb(self):
        self.verb_obj.human_readable

    @property
    def verb_obj(self):
        if self.verb not in activity.schema_verbs:
            raise activity.UnknownActivityError("Unknown verb: %s" % (self.verb,))
        return activity.schema_verbs[self.verb]

    def __unicode__(self):
        name = self.actor
        if name.get_full_name() not in '':
            name = self.actor.get_full_name()
        r = u"%s %s %s" % (name, self.verb_obj.past_tense, self.obj)
        if self.target:
            r += u" on %s" % (self.target,)
        return r 

    def get_absolute_url(self):
        return reverse('activity.views.index', kwargs=dict(activity_id=self.id))
    
    def timesince(self, now=None):
        t = timesince(self.timestamp, now)
        c = lambda x: x == "0 minutes" and _("less than a minute") or x
        return c(t)
