from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.utils.timesince import timesince 

from activity import humanize_verb

class ActivityManager(models.Manager):
    def from_user(self, user, limit=None):
        if not isinstance(user, User):
            return []
        activities = self.filter(actor=user).order_by('-timestamp')
        if limit:
            activities = activities[:limit]
        return activities

    def from_object(self, obj, limit=None):
        if not isinstance(obj, models.Model):
            return []
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
        if self.target:
            return u'%s %s %s %s ago' % \
                   (self.actor, humanize_verb(self.verb), self.target, self.timesince())
        return u'%s %s %s %s ago' % (self.actor, humanize_verb(self.verb), self.obj, self.timesince())

    def timesince(self, now=None):
        return timesince(self.timestamp, now)    
