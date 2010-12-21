import datetime
import logging

from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import ugettext as _

from users.models import UserProfile
from drumbeat.models import ModelBase
from projects.models import Project

log = logging.getLogger(__name__)


class Relationship(ModelBase):
    """
    A relationship between two objects. Source is usually a user but can
    be any ```Model``` instance. Target can also be any ```Model``` instance.
    """
    source = models.ForeignKey(
        UserProfile, related_name='source_relationships')
    target_user = models.ForeignKey(UserProfile, null=True, blank=True)
    target_project = models.ForeignKey(Project, null=True, blank=True)

    created_on = models.DateTimeField(
        auto_now_add=True, default=datetime.date.today())

    def save(self, *args, **kwargs):
        """Check that the source and the target are not the same user."""
        if (self.source == self.target_user):
            raise ValidationError(
                _('Cannot create self referencing relationship.'))
        super(Relationship, self).save(*args, **kwargs)

    class Meta:
        unique_together = ('source', 'target_user')

    def __unicode__(self):
        return "%(from)r => %(to)r" % {
            'from': repr(self.source),
            'to': repr(self.target_user or self.target_project),
        }


#################
# Duck Punching #
#################


def followers(obj):
    """
    Return a list of ```UserProfile``` objects that follow ```obj```.
    Note that ```obj``` can be a ```UserProfile``` or ```Project```
    instance.
    """
    kwargs = {'target_user': obj}
    if isinstance(obj, Project):
        kwargs = {'target_project': obj}
    relationships = Relationship.objects.filter(**kwargs)
    return [rel.source for rel in relationships]


def following(user, model=UserProfile):
    """
    Return a list of objects that ```user``` is following. All objects returned
    will be ```Project``` or ```UserProfile``` instances. Optionally filter by
    type by including a ```model``` parameter.
    """
    relationships = Relationship.objects.filter(source=user)
    if isinstance(model, Project) or model == Project:
        return [rel.target_project for
                rel in relationships.exclude(target_project__isnull=True)]
    return [rel.target_user for
            rel in relationships.exclude(target_user__isnull=True)]


def is_following(obj, model):
    """Determine whether ```obj``` is following ```model```."""
    return model in obj.following(model=model)

UserProfile.followers = followers
UserProfile.following = following
UserProfile.is_following = is_following
Project.followers = followers

admin.site.register(Relationship)

###########
# Signals #
###########


def project_creation_handler(sender, **kwargs):
    project = kwargs.get('instance', None)
    created = kwargs.get('created', False)

    if not created or not isinstance(project, Project):
        return

    rel = Relationship(source=project.created_by,
                       target_project=project)
    rel.save()


def follow_handler(sender, **kwargs):
    rel = kwargs.get('instance', None)
    if not isinstance(rel, Relationship):
        return
    try:
        import activity
        if rel.target_user:
            activity.send(rel.source.user, 'follow', rel.target_user.user)
        else:
            activity.send(rel.source.user, 'follow', rel.target_project)
    except ImportError:
        pass


post_save.connect(project_creation_handler, sender=Project)
post_save.connect(follow_handler, sender=Relationship)
