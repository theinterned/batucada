import datetime
import logging

from django.contrib import admin
from django.db import models


from drumbeat.models import ModelBase
from projects.models import Project 

import caching.base

log = logging.getLogger(__name__)

class Challenge(ModelBase):
    """ Inovation (design) Challenges """
    title = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    description_html = models.TextField(null=True, blank=True)

    slug = models.SlugField(unique=True)
    
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    project = models.ForeignKey(Project)
    created_by = models.ForeignKey('users.UserProfile', 
                                   related_name='challenges')

    is_open = models.BooleanField()

class Submission(ModelBase):
    """ A submitted entry for a Challenge """ 
    title = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    description_html = models.TextField(null=True, blank=True)

    slug = models.SlugField(unique=True)    

    challenge = models.ManyToManyField(Challenge)
    created_by = models.ForeignKey('users.UserProfile',
                                   related_name='submissions')
