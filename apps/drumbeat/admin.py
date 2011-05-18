from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.contrib.comments.models import Comment

from django_openid_auth.models import Nonce, Association

from djcelery.models import TaskState, PeriodicTask, CrontabSchedule, IntervalSchedule, WorkerState
from taggit.models import Tag
from wellknown.models import Resource
from voting.models import Vote


print admin.site._registry


admin.site.unregister([Group, User, Comment, Nonce, Association,
    TaskState, PeriodicTask, CrontabSchedule, IntervalSchedule, WorkerState,
    Tag, Resource, Vote])
