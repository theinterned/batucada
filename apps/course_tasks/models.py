import datetime
from markdown import markdown
from bleach import Bleach

from django.contrib import admin
from django.db import models
from django.db.models.signals import post_save
from django.utils.timesince import timesince
from django.utils.html import urlize
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from activity.models import Activity
from drumbeat.models import ModelBase

TAGS = ('a', 'b', 'em', 'i', 'strong', 'p')


class CourseTask(ModelBase):
    object_type = 'http://activitystrea.ms/schema/1.0/event'

    author = models.ForeignKey('users.UserProfile')
    project = models.ForeignKey('projects.Project', null=True, blank=True)
    title = models.CharField(max_length=150)
    description = models.CharField(max_length=1000)
    created_on = models.DateTimeField(
        auto_now_add=True, default=datetime.date.today())
    due_on = models.DateField(null=True, blank=True)

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('task_show', (), {
            'task_id': self.pk,
        })

    def timesince(self, now=None):
        return timesince(self.created_on, now)

    def friendly_verb(self):
        return mark_safe(_('Posted a task %s') % self.title)

    def representation(self):
        if self.due_on:
            return mark_safe("%(desc)s Due on %(due)s" % {'desc': self.description, 'due': self.due_on})
        else:
            return mark_safe(self.description)

admin.site.register(CourseTask)


def task_creation_handler(sender, **kwargs):
    task = kwargs.get('instance', None)
    created = kwargs.get('created', False)

    if not created or not isinstance(task, CourseTask):
        return

    # convert task body to markdown and bleachify
    bl = Bleach()
    task.title = urlize(task.title)
    task.description = urlize(task.description)
    task.title = bl.clean(markdown(task.title), tags=TAGS)
    task.description = bl.clean(markdown(task.description), tags=TAGS)
    task.save()

    # fire activity
    activity = Activity(
        actor=task.author,
        verb='http://activitystrea.ms/schema/1.0/post',
        target_object=task,
    )
    if task.project:
        activity.target_project = task.project
    activity.save()

post_save.connect(task_creation_handler, sender=CourseTask)

