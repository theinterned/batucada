from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import pre_save, pre_delete
from django.utils.translation import ugettext as _

import activity

class Relationship(models.Model):
    source_content_type = models.ForeignKey(ContentType, related_name='source_relationships')
    source_object_id = models.PositiveIntegerField()
    source = generic.GenericForeignKey('source_content_type', 'source_object_id')

    target_content_type = models.ForeignKey(ContentType, related_name='target_relationships')
    target_object_id = models.PositiveIntegerField()
    target = generic.GenericForeignKey('target_content_type', 'target_object_id')
    
    def save(self, *args, **kwargs):
        if (self.source_content_type == self.target_content_type) and (
            self.source.pk == self.target.pk):
            raise ValidationError(_('Cannot create self referencing relationship.'))
        super(Relationship, self).save(*args, **kwargs)

    class Meta:
        unique_together = ('source_content_type', 'target_content_type',
                           'source_object_id', 'target_object_id',)

    def __unicode__(self):
        return "%(from)s => %(to)s" % {
            'from': self.source,
            'to': self.target
        }

def followers(self):
    return [rel.source for rel in Relationship.objects.filter(
        target_object_id=self.id).filter(
                target_content_type=ContentType.objects.get_for_model(self))]

def following(self):
    return [rel.target for rel in Relationship.objects.filter(
        source_object_id=self.id).filter(
                source_content_type=ContentType.objects.get_for_model(self))]

def is_following(self, model):
    obj_type_id = ContentType.objects.get_for_model(model)
    return len(Relationship.objects.filter(
        source_object_id=self.id,
        target_object_id=model.pk,
        target_content_type=obj_type_id)) > 0

User.followers = followers
User.following = following
User.is_following = is_following

def follow_handler(sender, **kwargs):
    rel = kwargs.get('instance', None)
    if not isinstance(rel, Relationship):
        return
    activity.send(rel.source, 'follow', rel.target)

pre_save.connect(follow_handler, sender=Relationship)
