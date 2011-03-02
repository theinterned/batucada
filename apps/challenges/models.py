from datetime import datetime
import logging

from django.contrib import admin
from django.db import models
from django.template.defaultfilters import slugify

from drumbeat.models import ModelBase
from projects.models import Project 

import caching.base

log = logging.getLogger(__name__)

class ChallengeManager(caching.base.CachingManager):
    def active(self, project_id=0):
        q = Challenge.objects.filter(start_date__lte=datetime.now()).filter(end_date__gte=datetime.now())
        if project_id:
            q = q.filter(id=project_id)
        return q


class Challenge(ModelBase):
    """ Inovation (design) Challenges """
    title = models.CharField(max_length=100, unique=True)

    description = models.TextField()
    description_html = models.TextField(null=True, blank=True)

    slug = models.SlugField(unique=True)
    
    start_date = models.DateTimeField(default=datetime.now())
    end_date = models.DateTimeField()

    project = models.ForeignKey(Project)
    created_by = models.ForeignKey('users.UserProfile', 
                                   related_name='challenges')
    created_on = models.DateTimeField(
        auto_now_add=True, default=datetime.now())
    

    is_open = models.BooleanField()

    objects = ChallengeManager()

    def is_active(self):
        return self.start_date < datetime.now() and self.end_date > datetime.now()

    def save(self):
        """Make sure each challenge has a unique slug."""
        count = 1
        if not self.slug:
            slug = slugify(self.title)
            self.slug = slug
            while True:
                existing = Challenge.objects.filter(slug=self.slug)
                if len(existing) == 0:
                    break
                self.slug = slug + str(count)
                count += 1
        super(Challenge, self).save()
admin.site.register(Challenge)    

class Submission(ModelBase):
    """ A submitted entry for a Challenge """ 
    title = models.CharField(max_length=100, unique=True)
    summary = models.TextField()    
    description = models.TextField()
    description_html = models.TextField(null=True, blank=True)

    challenge = models.ManyToManyField(Challenge)
    created_by = models.ForeignKey('users.UserProfile',
                                   related_name='submissions')
    created_on = models.DateTimeField(
        auto_now_add=True, default=datetime.now())
    
admin.site.register(Submission)


class Judge(ModelBase):
    challenge = models.ForeignKey(Challenge)
    user = models.ForeignKey('users.UserProfile',
                                   related_name='judges')


    class Meta:
        unique_together = ( ('challenge', 'user'), )

    
admin.site.register(Judge)


### Signals


