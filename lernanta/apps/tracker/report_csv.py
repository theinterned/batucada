from django.db.models import Q
from django.contrib.contenttypes.models import ContentType

from projects.models import Project, Participation, PerUserTaskCompletion
from tracker.models import PageView
from badges.models import Badge, Award, Assessment, Submission
from statuses.models import Status
from replies.models import PageComment
from users.models import UserProfile
from l10n import locales
from content.models import Page
from schools.models import School, ProjectSet

# INPUT
# group (slug or shortname of groups, courses, challenges)
GROUPS_PATH = 'groups.csv'

# OUTPUT
# url, access_date, ip_address, user_id
VISITS_PATH = 'visits_data.csv'
# group, userid, start_date, leave_date, role (learner, adopter, creator)
PARTICIPATIONS_PATH = 'participations_data.csv'
# group, task
TASKS_PATH = 'tasks_data.csv'
# group, task, userid, checked_date, unchecked_date
TASKS_COMPLETION_PATH = 'tasks_completion_data.csv'
# type, badge, group
BADGES_GROUPS_PATH = 'badges_groups_data.csv'
# type, badge, userid, date
AWARDS_PATH = 'awards_data.csv'
# type, badge, userid (assessor), submission (yes or no), date
ASSESSMENTS_PATH = 'assessments_data.csv'
# type, badge, userid, date
SUBMISSIONS_PATH = 'submissions_data.csv'
# group, task, userid, date
COMMENTS_PATH = 'comments_data.csv'


def read_csv(path):
    data = []
    with open(path) as f:
        for line in f:
            data.append(tuple(line.strip().split(',')))
    return data


def get_page_filters(projects):
    tracked_urls = set()
    tracked_url_prefixes = set()
    for project in projects:
        tracked_url_prefixes.add(project.get_absolute_url())
        if project.school:
            tracked_urls.add(project.school.get_absolute_url())
        for projectset in project.projectsets.all():
            tracked_urls.add(projectset.get_absolute_url())
    page_filters = None
    for prefix in tracked_url_prefixes:
        if page_filters:
            page_filters |= Q(request_url__startswith=prefix)
        else:
            page_filters = Q(request_url__startswith=prefix)
        for k in locales.LOCALES:
            prefix_with_locale = '/%s%s' % (locales.LOCALES[k].external, prefix)
            page_filters |= Q(request_url__startswith=prefix_with_locale)
    for url in tracked_urls:
        page_filters |= Q(request_url=url)
        for k in locales.LOCALES:
            url_with_locale = '/%s%s' % (locales.LOCALES[k].external, url)
            page_filters |= Q(request_url=url_with_locale)
    return page_filters


def generate_csv_files():
    groups_slugs = [r[0] for r in read_csv(GROUPS_PATH)]
    projects = Project.objects.filter(slug__in=groups_slugs)
    page_filters = get_page_filters(projects)
    projects = projects.values('id')
    with open(VISITS_PATH, 'w') as f:
        for pageview in PageView.objects.filter(page_filters).distinct():
            if pageview.user:
                f.write('%s,%s,%s,%s\n' % (pageview.request_url, pageview.access_time, pageview.ip_address, 'user%s' % pageview.user.id))
            else:
                f.write('%s,%s,%s,\n' % (pageview.request_url, pageview.access_time, pageview.ip_address))
    groups_slugs = [r[0] for r in read_csv(GROUPS_PATH)]
    projects = Project.objects.filter(slug__in=groups_slugs).values('id')
    with open(PARTICIPATIONS_PATH, 'w') as f:
        for part in Participation.objects.filter(project__in=projects).distinct():
            status = 'learner'
            if part.organizing:
                status='creator'
            elif part.adopter:
                status = 'adopter'
            f.write('%s,%s,%s,%s,%s\n' % (part.project.slug, 'user%s' % part.user.id, part.joined_on, part.left_on or '', status))
    with open(TASKS_PATH, 'w') as f:
        for task in Page.objects.filter(project__in=projects, listed=True, deleted=False).distinct():
            f.write('%s,%s\n' % (task.project.slug, task.slug))
    with open(TASKS_COMPLETION_PATH, 'w') as f:
        for comp in PerUserTaskCompletion.objects.filter(page__project__in=projects, page__deleted=False).distinct():
            f.write('%s,%s,%s,%s,%s\n' % (comp.page.project.slug, comp.page.slug, 'user%s' % comp.user.id, comp.checked_on, comp.unchecked_on or ''))
    with open(BADGES_GROUPS_PATH, 'w') as f:
        for project in Project.objects.filter(id__in=projects).distinct():
            for badge in project.badges.all():
                f.write('%s,%s,%s\n' % (badge.logic, badge.slug, project.slug))
    with open(AWARDS_PATH, 'w') as f:
        for award in Award.objects.filter(badge__groups__in=projects).distinct():
            f.write('%s,%s,%s,%s\n' % (award.badge.logic, award.badge.slug, 'user%s' % award.user.id, award.awarded_on))
    with open(ASSESSMENTS_PATH, 'w') as f:
        for assessment in Assessment.objects.filter(badge__groups__in=projects).distinct():
            f.write('%s,%s,%s,%s,%s\n' % (assessment.badge.logic, assessment.badge.slug, 'user%s' % assessment.assessor.id,
                'yes' if assessment.submission else 'no', assessment.created_on))
    with open(SUBMISSIONS_PATH, 'w') as f:
        for sub in Submission.objects.filter(badge__groups__in=projects).distinct():
            f.write('%s,%s,%s,%s\n' % (sub.badge.logic, sub.badge.slug, 'user%s' % sub.author.id, sub.created_on))
    with open(COMMENTS_PATH, 'w') as f:
        project_ct = ContentType.objects.get_for_model(Project)
        status_ct = ContentType.objects.get_for_model(Status)
        task_ct = ContentType.objects.get_for_model(Page)
        for status in Status.objects.filter(project__in=projects).distinct():
            f.write('%s,,%s,%s\n' % (status.project.slug, 'user%s' % status.author.id, status.created_on))
        comments = PageComment.objects.filter(scope_content_type=project_ct, scope_id__in=projects)
        for comment in comments.filter(page_content_type=status_ct).distinct():
            f.write('%s,,%s,%s\n' % (comment.scope_object.slug, 'user%s' % comment.author.id, comment.created_on))
        for comment in comments.filter(page_content_type=task_ct).distinct():
            f.write('%s,%s,%s,%s' % (comment.scope_object.slug, comment.page_object.slug, 'user%s' % comment.author.id, comment.created_on))


def test_generated_csv_files():
    for path in [VISITS_PATH, PARTICIPATIONS_PATH, TASKS_PATH, TASKS_COMPLETION_PATH,
           BADGES_GROUPS_PATH, AWARDS_PATH, ASSESSMENTS_PATH, SUBMISSIONS_PATH, COMMENTS_PATH]:
        data = read_csv(path)
        print path, len(data), len(set(data)), '-'*10, data[0]

