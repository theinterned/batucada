import datetime
import logging

from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models, IntegrityError
from django.db.models.signals import post_save
from django.utils.translation import ugettext as _

log = logging.getLogger(__name__)


class Relationship(models.Model):
    """
    A relationship between two objects. Source is usually a user but can
    be any ```Model``` instance. Target can also be any ```Model``` instance.
    """
    source_content_type = models.ForeignKey(
        ContentType, related_name='source_relationships')
    source_object_id = models.PositiveIntegerField()
    source = generic.GenericForeignKey(
        'source_content_type', 'source_object_id')

    target_content_type = models.ForeignKey(
        ContentType, related_name='target_relationships')
    target_object_id = models.PositiveIntegerField()
    target = generic.GenericForeignKey(
        'target_content_type', 'target_object_id')

    created_on = models.DateTimeField(
        auto_now_add=True, default=datetime.date.today())

    def save(self, *args, **kwargs):
        """Check that the source and the target are not the same object."""
        if (self.source == self.target):
            raise ValidationError(
                _('Cannot create self referencing relationship.'))
        # redundant check for databases that don't support
        # multi-column UNIQUE constraints
        existing = Relationship.objects.filter(
            source_content_type__exact=self.source_content_type,
            source_object_id__exact=self.source_object_id,
            target_content_type__exact=self.target_content_type,
            target_object_id__exact=self.target_object_id).count()
        if existing > 0:
            raise IntegrityError('Duplicate Entry')
        super(Relationship, self).save(*args, **kwargs)

    class Meta:
        unique_together = ('source_content_type', 'target_content_type',
                           'source_object_id', 'target_object_id',)

    def __unicode__(self):
        return "%(from)s => %(to)s" % {
            'from': self.source,
            'to': self.target,
        }


#################
# Duck Punching #
#################

def followers(obj):
    """
    Return a list of ```User``` objects that follow ```obj```.
    Note that ```obj``` can be any ```Model``` instance.
    """
    relationships = Relationship.objects.filter(
        target_object_id=obj.id,
        target_content_type=ContentType.objects.get_for_model(obj))
    return [rel.source for rel in relationships]


def followers_count(obj):
    """
    Return the number of followers belonging to ```obj```.
    Note that ```obj``` can be any ```Model``` instance.
    """
    return len(obj.followers())


def following(obj):
    """
    Return a list of objects that ```obj``` is following. All objects returned
    will be ```Model``` instances.
    """
    content_type = ContentType.objects.get_for_model(obj)
    relationships = Relationship.objects.filter(
        source_object_id=obj.id, source_content_type=content_type)
    return [rel.target for rel in relationships]


def following_count(obj):
    """Return the number of objects that ```obj``` is following."""
    return len(obj.following())


def is_following(obj, model):
    """Determine whether ```obj``` is following ```model```."""
    return model in obj.following()

User.followers = followers
User.followers_count = followers_count
User.following = following
User.following_count = following_count
User.is_following = is_following


admin.site.register(Relationship)

###########
# Signals #
###########


def follow_handler(sender, **kwargs):
    rel = kwargs.get('instance', None)
    if not isinstance(rel, Relationship):
        return
    try:
        import activity
        activity.send(rel.source, 'follow', rel.target)
    except ImportError:
        pass


post_save.connect(follow_handler, sender=Relationship)
