import csv

from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.contrib.comments.models import Comment
from django.contrib.sites.models import Site
from django.utils.translation import ugettext as _
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse

from django_openid_auth.models import Nonce, Association, UserOpenID
from djcelery.models import TaskState, PeriodicTask, CrontabSchedule
from djcelery.models import IntervalSchedule, WorkerState
from taggit.models import Tag
from wellknown.models import Resource
from voting.models import Vote
from drumbeatmail.models import Message


admin.site.unregister([Group, User, Comment, Nonce, Association, UserOpenID,
    TaskState, PeriodicTask, CrontabSchedule, IntervalSchedule, WorkerState,
    Tag, Resource, Vote, Site])


admin.site._registry[Message].date_hierarchy = 'sent_at'
admin.site._registry[Message].list_display = ('id', 'subject', 'sender',
    'recipient', 'sent_at')
admin.site._registry[Message].list_filter = ('sent_at',)
admin.site._registry[Message].search_fields = ('id', 'subject', 'body',
    'sender__username', 'recipient__username')


def export_as_csv(modeladmin, request, queryset):
    """
    Generic csv export admin action.
    """
    if not request.user.is_staff:
        raise PermissionDenied
    opts = modeladmin.model._meta
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s.csv' % unicode(
        opts).replace('.', '_')
    writer = csv.writer(response)
    field_names = [field.name for field in opts.fields]
    # Write a first row with header information
    writer.writerow(field_names)
    # Write data rows
    for obj in queryset:
        writer.writerow([getattr(obj, field) for field in field_names])
    return response
export_as_csv.short_description = _("Export selected objects as csv file")
