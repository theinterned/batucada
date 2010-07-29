from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext as _

class UserRelationship(models.Model):
    from_user = models.ForeignKey(User, unique=False, related_name='from_user')
    to_user = models.ForeignKey(User, unique=False, related_name='to_user')

    def save(self, *args, **kwargs):
        if self.from_user.id == self.to_user.id:
            raise ValidationError(_('User cannot follow oneself.'))
        super(UserRelationship, self).save(*args, **kwargs)

    class Meta:
        unique_together = (('from_user', 'to_user'),)

    @classmethod
    def get_relationships_from(cls, user):
        return [u.to_user.id for u in cls.objects.filter(
            from_user__exact=user.id)]

    @classmethod
    def get_relationships_to(cls, user):
        return [u.from_user.id for u in cls.objects.filter(
            to_user__exact=user.id)]

