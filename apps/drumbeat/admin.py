from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.contrib.comments.models import Comment
from django.contrib.sites.models import Site

from django_openid_auth.models import Nonce, Association, UserOpenID
from djcelery.models import TaskState, PeriodicTask, CrontabSchedule, IntervalSchedule, WorkerState
from taggit.models import Tag
from wellknown.models import Resource
from voting.models import Vote
from drumbeatmail.models import Message


admin.site.unregister([Group, User, Comment, Nonce, Association, UserOpenID,
    TaskState, PeriodicTask, CrontabSchedule, IntervalSchedule, WorkerState,
    Tag, Resource, Vote, Site])


admin.site._registry[Message].date_hierarchy = 'sent_at'
admin.site._registry[Message].list_display = ('id', 'subject', 'sender', 'recipient', 'sent_at')
admin.site._registry[Message].list_filter = ('sent_at',)
admin.site._registry[Message].search_fields = ('id', 'subject', 'body', 'sender__username', 'recipient__username')



