import logging
import datetime
import calendar

from django.shortcuts import render_to_response
from django.template import RequestContext
from django import http

from users.models import UserProfile
from replies.models import PageComment
from projects.models import Participation, Project

log = logging.getLogger(__name__)


def get_time_details():
    stats_date = datetime.datetime.now()
    today = stats_date.date()
    number_days_month = calendar.monthrange(
        today.year, today.month)[1]
    prev_month = (today.month - 1) if today.month > 1 else 12
    prev_month_year = today.year if today.month > 1 \
        else (today.year - 1)
    return {
        'day': today.day,
        'month': today.month,
        'year': today.year,
        'number_days_month': number_days_month,
        'prev_month': prev_month,
        'prev_month_year': prev_month_year,
        'stats_date': stats_date,
    }


def get_stats(name, model_cls, date_field_name, time_details):
    todays_count = model_cls.objects.filter(**{
        date_field_name + '__day': time_details['day'],
        date_field_name + '__month': time_details['month'],
        date_field_name + '__year': time_details['year']
        }).count()

    this_month_count = model_cls.objects.filter(**{
        date_field_name + '__month': time_details['month'],
        date_field_name + '__year': time_details['year']
        }).count()

    pace = this_month_count * time_details['number_days_month']
    days_passed = time_details['day'] - 1
    if days_passed > 0:
        pace = pace / days_passed

    prev_month_count = model_cls.objects.filter(**{
        date_field_name + '__month': time_details['prev_month'],
        date_field_name + '__year': time_details['prev_month_year']
        }).count()

    green_threshold = prev_month_count * 105 / 100
    red_threshold = prev_month_count * 95 / 100

    if pace > green_threshold:
        status_color = 'green'
    elif pace < red_threshold:
        status_color = 'red'
    else:
        status_color = 'white'

    return {
        'name': name,
        'today': todays_count,
        'this_month': this_month_count,
        'pace': pace,
        'prev_month': prev_month_count,
        'status_color': status_color,
    }


def scoreboard(request):
    if not request.user.is_authenticated() or not request.user.is_staff:
        raise http.Http404
    time_details = get_time_details()
    users_stats = get_stats('users', UserProfile, 'user__date_joined', time_details)
    comments_stats = get_stats('comments', PageComment, 'created_on', time_details)
    joins_stats = get_stats('joins', Participation, 'joined_on', time_details)
    groups_stats = get_stats('groups', Project, 'created_on', time_details)
    context = {
        'stats': [users_stats, comments_stats, joins_stats, groups_stats],
        'stats_date': time_details['stats_date'],
    }
    return render_to_response(
        'tracker/scoreboard.html', context,
        context_instance=RequestContext(request)
    )
