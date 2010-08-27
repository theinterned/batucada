from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.utils.timesince import timesince
from django.utils.translation import ugettext as _

from activity import humanize_verb
from l10n.urlresolvers import reverse

class ActivityManager(models.Manager):
    def from_user(self, user, limit=None):
        activities = self.filter(actor=user).order_by('-timestamp')
        if limit:
            activities = activities[:limit]
        return activities

    def from_object(self, obj, limit=None):
        activities = self.filter(obj=obj).order_by('-timestamp')
        if limit:
            activities = activities[:limit]
        return activities
    
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
    
    def __unicode__(self):
        r = u"%s %s %s" % (self.actor, humanize_verb(self.verb), self.obj)
        if self.target:
            r += u" on %s" % (self.target,)
        return r + _(" %(timesince)s ago") % {'timesince': self.timesince()}

    def get_absolute_url(self):
        return reverse('activity.views.index', kwargs=dict(activity_id=self.id))
    
    def timesince(self, now=None):
        t = timesince(self.timestamp, now)
        c = lambda x: x == "0 minutes" and _("less than a minute") or x
        return c(t)
