from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import pre_save, pre_delete
from django.utils.translation import ugettext as _

from activity import action

class UserRelationship(models.Model):
    from_user = models.ForeignKey(User, unique=False, related_name='from_user_rels')
    to_user = models.ForeignKey(User, unique=False, related_name='to_user_rels')

    def save(self, *args, **kwargs):
        if self.from_user.id == self.to_user.id:
            raise ValidationError(_('User cannot follow oneself.'))
        super(UserRelationship, self).save(*args, **kwargs)

    class Meta:
        unique_together = (('from_user', 'to_user'),)

    def __unicode__(self):
        return "%(from)s => %(to)s" % {
            'from': self.from_user.username,
            'to': self.to_user.username
        }

class UserMixin(object):
    def followers(self):
        return [rel.from_user for rel in self.to_user_rels.all()]

    def following(self):
        return [rel.to_user for rel in self.from_user_rels.all()]

if len(User.__bases__) == 1:
    User.__bases__ += (UserMixin,)

def follow_handler(sender, **kwargs):
    rel = kwargs.get('instance', None)
    if not isinstance(rel, UserRelationship):
        return
    action.send(rel.from_user, 'follow', rel.to_user)

pre_save.connect(follow_handler, sender=UserRelationship)
