import logging
import datetime

from django.db import models

from drumbeat.models import ModelBase
from richtext.models import RichTextField

log = logging.getLogger(__name__)


class Reviewer(ModelBase):
    user = models.ForeignKey('users.UserProfile')
    can_delete = models.BooleanField()
    can_feature = models.BooleanField()

    def __unicode__(self):
        return unicode(self.user)


class Review(ModelBase):

    project = models.ForeignKey('projects.Project', related_name='reviews')
    author = models.ForeignKey('users.UserProfile', related_name='reviews')
    accepted = models.BooleanField(default=False)
    mark_deleted = models.BooleanField(default=False)
    mark_featured = models.BooleanField(default=False)
    content = RichTextField(config_name='rich', blank=False)
    created_on = models.DateTimeField(auto_now_add=True,
        default=datetime.datetime.now)

    def __unicode__(self):
        return 'Review for %s' % self.project.name

    @models.permalink
    def get_absolute_url(self):
        return ('show_project_reviews', (), {
            'slug': self.project.slug,
        })

