import logging

from django.db import models

from drumbeat.models import ModelBase
from richtext.models import RichTextField

log = logging.getLogger(__name__)


class Reviewer(ModelBase):
    user = models.ForeignKey('users.UserProfile')

    def __unicode__(self):
        return unicode(self.user)


class Review(ModelBase):

    project = models.ForeignKey('projects.Project', related_name='reviews')
    author = models.ForeignKey('users.UserProfile', related_name='reviews')
    accepted = models.BooleanField(default=True)
    content = RichTextField(config_name='rich', blank='False')

    def __unicode__(self):
        return 'Review for %s' % self.project.name

