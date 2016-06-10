import datetime

from django import template
from django.template.defaultfilters import timesince
from django.utils.translation import ugettext as _

register = template.Library()


@register.filter
def time_since(activity):
    now = datetime.datetime.now()
    delta = now - activity.created_on
    if delta > datetime.timedelta(days=2):
        return activity.created_on.strftime("%d %b %Y")
    return timesince(activity.created_on) + _(" ago")
