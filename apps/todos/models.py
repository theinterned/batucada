import datetime
from markdown import markdown
from bleach import Bleach

from django.contrib import admin
from django.db import models
from django.db.models.signals import post_save
from django.utils.timesince import timesince
from django.utils.html import urlize

from activity.models import Activity
from drumbeat.models import ModelBase

TAGS = ('a', 'b', 'em', 'i', 'strong', 'p')


class Todo(ModelBase):
    object_type = 'http://activitystrea.ms/schema/1.0/event'

    author = models.ForeignKey('users.UserProfile')
    project = models.ForeignKey('projects.Project', null=True, blank=True)
    title = models.CharField(max_length=150)
    description = models.CharField(max_length=1000)
    created_on = models.DateTimeField(
        auto_now_add=True, default=datetime.date.today())
    due_on = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('todos_show', (), {
            'todo_id': self.pk,
        })

    def timesince(self, now=None):
        return timesince(self.created_on, now)

admin.site.register(Todo)


def todo_creation_handler(sender, **kwargs):
    todo = kwargs.get('instance', None)
    created = kwargs.get('created', False)

    if not created or not isinstance(todo, Todo):
        return

    # convert todo body to markdown and bleachify
    bl = Bleach()
    todo.title = urlize(todo.title)
    todo.description = urlize(todo.description)
    todo.title = bl.clean(markdown(todo.title), tags=TAGS)
    todo.description = bl.clean(markdown(todo.description), tags=TAGS)
    todo.save()

    # fire activity
    activity = Activity(
        actor=todo.author,
        verb='http://activitystrea.ms/schema/1.0/post',
        target_todo=todo,
    )
    if todo.project:
        activity.target_project = todo.project
    activity.save()

post_save.connect(todo_creation_handler, sender=Todo)

