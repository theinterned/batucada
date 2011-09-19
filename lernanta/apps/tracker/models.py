import datetime

from django.contrib.auth.models import User
from django.db import models
from django.contrib.contenttypes.models import ContentType

from drumbeat.models import ModelBase
from content.models import Page
from projects.models import Project
from activity.schema import verbs
from activity.models import Activity
from replies.models import PageComment

from tracker.utils import force_date


class PageView(ModelBase):
    session_key = models.CharField(max_length=100, db_index=True)
    user = models.ForeignKey(User, null=True, blank=True)
    access_time = models.DateTimeField(auto_now_add=True, db_index=True)
    request_url = models.CharField(max_length=755, db_index=True)
    referrer_url = models.URLField(
                         verify_exists=False,
                         db_index=True,
                         blank=True, null=True)
    ip_address = models.IPAddressField(
                         blank=True, null=True)
    time_on_page = models.IntegerField(blank=True, null=True)
    user_agent = models.CharField(max_length=255, blank=True, null=True)

    def __repr__(self):
        return '<Session: key %s, access time %s, request_url %s, time_on_page %s, user %s>' \
                % (self.session_key, self.access_time, self.request_url, self.time_on_page, self.user)


class PageViewMetrics(ModelBase):
    project = models.ForeignKey('projects.Project', related_name='pageview_metrics')
    user = models.ForeignKey(User, null=True, blank=True)
    ip_address = models.IPAddressField(blank=True, null=True)
    access_date = models.DateField()
    page_path = models.CharField(max_length=755)
    non_zero_length_time_on_page = models.PositiveIntegerField(null=True, blank=True)
    non_zero_length_pageviews = models.IntegerField(null=True, blank=True)
    zero_length_pageviews = models.IntegerField(null=True, blank=True)


def update_metrics_cache(project):
    # Only computes metrics for dates before today or yesterday
    # (depending on how early it is on the day).
    # This metrics are cacheable because they will not change
    # due to future pageviews.
    # Does not recompute cached metrics (i.e. also restricts how recent the dates
    # to process should be based on what we already have cached in the db).
    now = datetime.datetime.now()
    not_included_upper_bound = now.date()
    delta = datetime.timedelta(days=1)
    if now.hour < 2:
        not_included_upper_bound = not_included_upper_bound - delta
    try:
        last_cached_day = PageViewMetrics.objects.filter(project=project).order_by(
           '-access_date')[0].access_date
    except IndexError:
        last_cached_day = project.created_on - delta
    visits = PageView.objects.filter(access_time__gt=last_cached_day,
        access_time__lt=not_included_upper_bound)
    # Computes metrics for each page.
    pages = Page.objects.filter(project=project)
    for page in pages:
        page_path = 'groups/%s/content/%s/' % (project.slug, page.slug)
        # Filter page views to this page (does not include visits to subpages
        # like history/ and visits to older versions of this page).
        # Also adds the date for the visits as a separate field.
        pageviews = visits.filter(request_url__endswith=page_path).extra(
            select={'access_time_date': "date(access_time)"})
        # Computes time on page on for each date for each authenticated user not considering
        # zero length visits.
        # Excludes visits with unknow/NULL time_on_page so the sum does not become None.
        # Computes number of non-zero length visits.
        user_timeonpage_metrics = pageviews.exclude(user=None).exclude(
            time_on_page__isnull=True).values('user_id', 'access_time_date').annotate(
            models.Sum('time_on_page'), models.Count('id'))
        for metric in user_timeonpage_metrics:
            on_db_metric, created = PageViewMetrics.objects.get_or_create(project=project,
                user_id=metric['user_id'], access_date=metric['access_time_date'],
                page_path=page_path)
            on_db_metric.non_zero_length_time_on_page = metric['time_on_page__sum']
            on_db_metric.non_zero_length_pageviews = metric['id__count']
            if on_db_metric.zero_length_pageviews == None:
                on_db_metric.zero_length_pageviews = 0
            on_db_metric.save()
        # Computes number of zero-length visits for authenticated users (allows people
        # processing these metrics to add this count * a contant to the time on page counts
        # to give some weight to the zero-length visits).
        user_zero_length_visits_metrics = pageviews.exclude(user=None).filter(
            time_on_page__isnull=True).values('user_id', 'access_time_date').annotate(
            models.Count('id'))
        for metric in user_zero_length_visits_metrics:
            on_db_metric, created = PageViewMetrics.objects.get_or_create(project=project,
                user_id=metric['user_id'], access_date=metric['access_time_date'],
                page_path=page_path)
            on_db_metric.zero_length_pageviews = metric['id__count']
            if on_db_metric.non_zero_length_time_on_page == None:
                on_db_metric.non_zero_length_time_on_page = 0
            if on_db_metric.non_zero_length_pageviews == None:
                on_db_metric.non_zero_length_pageviews = 0
            on_db_metric.save()
        # Computes time on page on for each date for each unauthenticated visitor not considering
        # zero length visits.
        # Excludes visits with unknow/NULL time_on_page so the sum does not become None.
        # Computes number of non-zero length visits.
        unauth_visitor_timeonpage_metrics = pageviews.filter(user=None).exclude(
            time_on_page__isnull=True).values('ip_address', 'access_time_date').annotate(
            models.Sum('time_on_page'), models.Count('id'))
        for metric in unauth_visitor_timeonpage_metrics:
            on_db_metric, created = PageViewMetrics.objects.get_or_create(project=project,
                ip_address=metric['ip_address'], access_date=metric['access_time_date'],
                page_path=page_path)
            on_db_metric.non_zero_length_time_on_page = metric['time_on_page__sum']
            on_db_metric.non_zero_length_pageviews = metric['id__count']
            if on_db_metric.zero_length_pageviews == None:
                on_db_metric.zero_length_pageviews = 0
            on_db_metric.save()
        # Computes number of zero-length visits for unauthenticated visitors (allows people
        # processing these metrics to add this count * a contant to the time on page counts
        # to give some weight to the zero-length visits).
        unauth_visitor_zero_length_visits_metrics = pageviews.filter(user=None).filter(
            time_on_page__isnull=True).values('ip_address', 'access_time_date').annotate(
            models.Count('id'))
        for metric in unauth_visitor_zero_length_visits_metrics:
            on_db_metric, created = PageViewMetrics.objects.get_or_create(project=project,
                ip_address=metric['ip_address'], access_date=metric['access_time_date'],
                page_path=page_path)
            on_db_metric.zero_length_pageviews = metric['id__count']
            if on_db_metric.non_zero_length_time_on_page == None:
                on_db_metric.non_zero_length_time_on_page = 0
            if on_db_metric.non_zero_length_pageviews == None:
                on_db_metric.non_zero_length_pageviews = 0
            on_db_metric.save()


def get_metrics_axes(project):
    project_ct = ContentType.objects.get_for_model(Project)
    page_ct = ContentType.objects.get_for_model(Page)
    page_paths = PageViewMetrics.objects.filter(
        project=project).distinct().order_by(
        'page_path').values_list('page_path', flat=True)
    dates = set(PageViewMetrics.objects.filter(
        project=project).distinct().values_list('access_date', flat=True))
    dates.update(PageComment.objects.filter(scope_id=project.id,
        scope_content_type=project_ct).extra(
            select={'created_on_date': "date(created_on)"}).distinct().values_list(
            'created_on_date', flat=True))
    dates.update(Activity.objects.filter(target_content_type=page_ct,
            scope_object=project, verb=verbs['update']).extra(
            select={'created_on_date': "date(created_on)"}).distinct().values_list(
            'created_on_date', flat=True))
    dates = (force_date(d) for d in dates)
    dates = sorted(dates, reverse=True)
    return page_paths, dates


def get_user_metrics(project, users, dates, page_paths, overview=False):
    project_ct = ContentType.objects.get_for_model(Project)
    page_ct = ContentType.objects.get_for_model(Page)
    for user in users:
        row = [user.username]
        if overview:
            row.append(user.last_active or user.user.last_login)
        user_comments = PageComment.objects.filter(scope_id=project.id,
            scope_content_type=project_ct, author=user.user)
        user_task_edits = Activity.objects.filter(actor=user.user,
            target_content_type=page_ct, scope_object=project,
            verb=verbs['update'])
        if not overview:
            for date in dates:
                # "Time on Course Pages", "Non-Zero Length Views",
                # "Zero Length Views", "Comments", "Task Edits"
                metrics = PageViewMetrics.objects.filter(
                    user=user, project=project, access_date=date).aggregate(
                    models.Sum('non_zero_length_time_on_page'),
                    models.Sum('non_zero_length_pageviews'),
                    models.Sum('zero_length_pageviews'))
                row.append("%.2f" % ((metrics['non_zero_length_time_on_page__sum'] or 0) / 60.0))
                row.append(metrics['non_zero_length_pageviews__sum'] or 0)
                row.append(metrics['zero_length_pageviews__sum'] or 0)
                comments_count = user_comments.filter(created_on__year=date.year,
                    created_on__month=date.month, created_on__day=date.day).count()
                row.append(comments_count)
                task_edits_count = user_task_edits.filter(created_on__year=date.year,
                    created_on__month=date.month, created_on__day=date.day).count()
                row.append(task_edits_count)
                for page_path in page_paths:
                    # Time on Page, Non-Zero Length Views, Zero Length Views
                    try:
                        metrics = PageViewMetrics.objects.get(project=project, user=user,
                            page_path=page_path, access_date=date)
                        row.append("%.2f" % (metrics.non_zero_length_time_on_page / 60.0))
                        row.append(metrics.non_zero_length_pageviews)
                        row.append(metrics.zero_length_pageviews)
                    except:
                        row.extend([0] * 3)
        # Totals
        # "Time on Course Pages", "Non-Zero Length Views",
        # "Zero Length Views", "Comments", "Task Edits"
        metrics = PageViewMetrics.objects.filter(
            user=user, project=project).aggregate(
            models.Sum('non_zero_length_time_on_page'),
            models.Sum('non_zero_length_pageviews'),
            models.Sum('zero_length_pageviews'))
        if overview:
            # Sumarize total time on pages by stimating a one minute
            # for visits of unknow legth (i.e. zero-length visits).
            total_time_on_pages = (metrics['non_zero_length_time_on_page__sum'] or 0)
            total_time_on_pages += (metrics['zero_length_pageviews__sum'] or 0) * 60
            row.append("%.2f" % (total_time_on_pages / 60.0))
        else:
            row.append("%.2f" % ((metrics['non_zero_length_time_on_page__sum'] or 0) / 60.0))
            row.append(metrics['non_zero_length_pageviews__sum'] or 0)
            row.append(metrics['zero_length_pageviews__sum'] or 0)
        total_comments_count = user_comments.count()
        row.append(total_comments_count)
        total_task_edits_count = user_task_edits.count()
        row.append(total_task_edits_count)
        if not overview:
            # Time on Page, Non-Zero Length Views, Zero Length Views
            for page_path in page_paths:
                metrics = PageViewMetrics.objects.filter(project=project,
                    user=user, page_path=page_path).aggregate(
                    models.Sum('non_zero_length_time_on_page'),
                    models.Sum('non_zero_length_pageviews'),
                    models.Sum('zero_length_pageviews'))
                row.append("%.2f" % ((metrics['non_zero_length_time_on_page__sum'] or 0) / 60.0))
                row.append(metrics['non_zero_length_pageviews__sum'] or 0)
                row.append(metrics['zero_length_pageviews__sum'] or 0)
        yield row


def get_unauth_metrics(project, dates, page_paths):
    ip_addresses = PageViewMetrics.objects.filter(
        project=project, user=None).distinct().values_list(
        'ip_address', flat=True)

    for index, ip_address in enumerate(ip_addresses):
        row = ["Non-loggedin User %s" % index]
        for date in dates:
            # Time on course pages, comments, task edits
            metrics = PageViewMetrics.objects.filter(
                user=None, project=project, access_date=date,
                ip_address=ip_address).aggregate(
                models.Sum('non_zero_length_time_on_page'),
                models.Sum('non_zero_length_pageviews'),
                models.Sum('zero_length_pageviews'))
            row.append("%.2f" % ((metrics['non_zero_length_time_on_page__sum'] or 0) / 60.0))
            row.append(metrics['non_zero_length_pageviews__sum'] or 0)
            row.append(metrics['zero_length_pageviews__sum'] or 0)
            row.extend([0] * 2)
            for page_path in page_paths:
                # Time on Page, Non-Zero Length Views, Zero Length Views
                try:
                    metrics = PageViewMetrics.objects.get(project=project, user=None,
                        page_path=page_path, access_date=date, ip_address=ip_address)
                    row.append("%.2f" % (metrics.non_zero_length_time_on_page / 60.0))
                    row.append(metrics.non_zero_length_pageviews)
                    row.append(metrics.zero_length_pageviews)
                except:
                    row.extend([0] * 3)
        # Totals
        # Time on course pages, comments, task edits
        metrics = PageViewMetrics.objects.filter(
            user=None, project=project, ip_address=ip_address).aggregate(
            models.Sum('non_zero_length_time_on_page'),
            models.Sum('non_zero_length_pageviews'),
            models.Sum('zero_length_pageviews'))
        row.append("%.2f" % ((metrics['non_zero_length_time_on_page__sum'] or 0) / 60.0))
        row.append(metrics['non_zero_length_pageviews__sum'] or 0)
        row.append(metrics['zero_length_pageviews__sum'] or 0)
        row.extend([0] * 2)
        # Time on Page, Non-Zero Length Views, Zero Length Views
        for page_path in page_paths:
            metrics = PageViewMetrics.objects.filter(project=project,
                user=None, page_path=page_path, ip_address=ip_address).aggregate(
                models.Sum('non_zero_length_time_on_page'),
                models.Sum('non_zero_length_pageviews'),
                models.Sum('zero_length_pageviews'))
            row.append("%.2f" % ((metrics['non_zero_length_time_on_page__sum'] or 0) / 60.0))
            row.append(metrics['non_zero_length_pageviews__sum'] or 0)
            row.append(metrics['zero_length_pageviews__sum'] or 0)
        yield row
