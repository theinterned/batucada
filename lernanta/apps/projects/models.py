import logging
import datetime

from django.core.cache import cache
from django.core.validators import MaxLengthValidator
from django.conf import settings
from django.db import models
from django.db.models import Count, Max, Q
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save

from taggit.managers import TaggableManager

from l10n.urlresolvers import reverse
from drumbeat import storage
from drumbeat.utils import get_partition_id, safe_filename
from drumbeat.models import ModelBase
from relationships.models import Relationship
from activity.models import Activity, RemoteObject, register_filter
from activity.schema import object_types, verbs
from notifications.models import send_notifications_i18n
from richtext.models import RichTextField
from content.models import Page
from replies.models import PageComment
from tags.models import GeneralTaggedItem
from learn import models as learn_model

log = logging.getLogger(__name__)


def determine_image_upload_path(instance, filename):
    return "images/projects/%(partition)d/%(filename)s" % {
        'partition': get_partition_id(instance.pk),
        'filename': safe_filename(filename),
    }


class Project(ModelBase):
    """Placeholder model for projects."""
    object_type = object_types['group']

    name = models.CharField(max_length=100)

    short_name = models.CharField(max_length=20, null=True, blank=True)

    # Select kind of project (study group, course, or other)
    STUDY_GROUP = 'study group'
    COURSE = 'course'
    CHALLENGE = 'challenge'
    CATEGORY_CHOICES = (
        (STUDY_GROUP, _('Study Group -- group of people working ' \
                        'collaboratively to acquire and share knowledge.')),
        (COURSE, _('Course -- led by one or more organizers with skills on ' \
                   'a field who direct and help participants during their ' \
                   'learning.')),
        (CHALLENGE, _('Challenge -- series of tasks peers can engage in ' \
                      'to develop skills.'))
    )
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES,
        default=STUDY_GROUP, null=True, blank=False)

    tags = TaggableManager(through=GeneralTaggedItem, blank=True)
    language = models.CharField(max_length=16, choices=settings.LANGUAGES,
        default=settings.LANGUAGE_CODE)

    other = models.CharField(max_length=30, blank=True, null=True)
    other_description = models.CharField(max_length=150, blank=True, null=True)

    short_description = models.CharField(max_length=150)
    long_description = RichTextField(validators=[MaxLengthValidator(700)])

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    duration_hours = models.PositiveIntegerField(default=0, blank=True)
    duration_minutes = models.PositiveIntegerField(default=0, blank=True)

    school = models.ForeignKey('schools.School', related_name='projects',
        null=True, blank=True)

    detailed_description = models.ForeignKey('content.Page',
        related_name='desc_project', null=True, blank=True)

    image = models.ImageField(upload_to=determine_image_upload_path, null=True,
                              storage=storage.ImageStorage(), blank=True)

    slug = models.SlugField(unique=True, max_length=110)

    # this field is deprecated
    featured = models.BooleanField(default=False, verbose_name='staff favourite')

    # this field is deprecated
    community_featured = models.BooleanField(default=False, verbose_name='community pick')

    created_on = models.DateTimeField(
        auto_now_add=True, default=datetime.datetime.now)

    # Indicates a test course. Affects activities and notifications
    test = models.BooleanField(default=False)
    under_development = models.BooleanField(default=True)
    not_listed = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)

    clone_of = models.ForeignKey('projects.Project', blank=True, null=True,
        related_name='derivated_projects')

    imported_from = models.CharField(max_length=150, blank=True, null=True)

    next_projects = models.ManyToManyField('projects.Project',
        symmetrical=False, related_name='previous_projects', blank=True,
        null=True)
    # Stealth Badges awarded upon completion of all tasks.
    completion_badges = models.ManyToManyField('badges.Badge',
        null=True, blank=True, related_name='projects_completion')

    deleted = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('group')

    def __unicode__(self):
        return _('%(name)s %(kind)s') % dict(name=self.name,
            kind=self.kind.lower())

    @models.permalink
    def get_absolute_url(self):
        return ('projects_show', (), {
            'slug': self.slug,
        })

    def friendly_verb(self, verb):
        if verbs['post'] == verb:
            return _('created')

    @property
    def kind(self):
        return self.other.lower() if self.other else self.category

    def followers(self, include_deleted=False):
        relationships = Relationship.objects.all()
        if not include_deleted:
            relationships = relationships.filter(
                source__deleted=False)
        return relationships.filter(target_project=self,
            deleted=False)

    def previous_followers(self, include_deleted=False):
        """Return a list of users who were followers if this project."""
        relationships = Relationship.objects.all()
        if not include_deleted:
            relationships = relationships.filter(
                 source__deleted=False)
        return relationships.filter(target_project=self,
            deleted=True)

    def non_participant_followers(self, include_deleted=False):
        return self.followers(include_deleted).exclude(
            source__id__in=self.participants(include_deleted).values('user_id'))

    def participants(self, include_deleted=False):
        """Return a list of users participating in this project."""
        participations = Participation.objects.all()
        if not include_deleted:
            participations = participations.filter(user__deleted=False)
        return participations.filter(project=self,
            left_on__isnull=True)

    def non_organizer_participants(self, include_deleted=False):
        return self.participants(include_deleted).filter(organizing=False)

    def adopters(self, include_deleted=False):
        return self.participants(include_deleted).filter(Q(adopter=True) | Q(organizing=True))

    def non_adopter_participants(self, include_deleted=False):
        return self.non_organizer_participants(include_deleted).filter(
            adopter=False)

    def organizers(self, include_deleted=False):
        return self.participants(include_deleted).filter(organizing=True)

    def publish(self):
        """ Remove all test, under_development and closed signups from the course """
        self.test = False
        self.under_development = False
        self.save()

        if self.category == self.COURSE:
            signup = self.sign_up.get()
            if signup.is_closed():
                signup.set_unmoderated_signup()

    def is_organizing(self, user):
        if user.is_authenticated():
            profile = user.get_profile()
            is_organizer = self.organizers().filter(user=profile).exists()
            is_superuser = user.is_superuser
            return is_organizer or is_superuser
        else:
            return False

    def is_following(self, user):
        if user.is_authenticated():
            profile = user.get_profile()
            is_following = self.followers().filter(source=profile).exists()
            return is_following
        else:
            return False

    def is_participating(self, user):
        if user.is_authenticated():
            profile = user.get_profile()
            is_organizer_or_participant = self.participants().filter(
                user=profile).exists()
            is_superuser = user.is_superuser
            return is_organizer_or_participant or is_superuser
        else:
            return False

    def get_metrics_permissions(self, user):
        """Provides metrics related permissions for metrics overview
        and CSV download."""
        if user.is_authenticated():
            if user.is_superuser:
                return True
            if self.is_organizing(user):
                return True
            if not self.school:
                return False
            is_school_organizer = self.school.organizers.filter(
                id=user.id).exists()
            if is_school_organizer:
                return True
        return False

    def get_metric_csv_permission(self, user):
        """Provides metrics related permissions for metrics CSV download."""
        if user.is_authenticated():
            # check for explicit permission grant
            csv_downloaders = settings.STATISTICS_CSV_DOWNLOADERS
            profile = user.get_profile()
            if profile.username in csv_downloaders:
                return True
            return self.get_metrics_permissions(user)
        return False

    def activities(self):
        return Activity.objects.filter(deleted=False,
            scope_object=self).order_by('-created_on')

    def create(self):
        self.save()
        self.send_creation_notification()

    def update_learn_api(self):
        if not self.pk:
            return
        try:
            learn_model.update_course_listing(**self.get_learn_api_data())
        except:
            learn_model.add_course_listing(**self.get_learn_api_data())

        course_url = reverse('projects_show', kwargs={'slug': self.slug})
        course_lists = learn_model.get_lists_for_course(course_url)
        list_names = [ l['name'] for l in course_lists ]
        if self.not_listed or self.test:
            for list_name in list_names:
                learn_model.remove_course_from_list(course_url, list_name)
        else:
            desired_list = 'drafts'
            if not (self.under_development or self.archived):
                desired_list = 'listed'
            elif self.archived:
                desired_list = 'archived'
            possible_lists = ['drafts', 'listed', 'archived']
            possible_lists.remove(desired_list)
            for l in possible_lists:
                if l in list_names:
                    learn_model.remove_course_from_list(course_url, l)
            if desired_list not in list_names:
                learn_model.add_course_to_list(course_url, desired_list)


    def save(self):
        """Make sure each project has a unique slug."""
        count = 1
        if not self.slug:
            slug = slugify(self.name)
            self.slug = slug
            while True:
                existing = Project.objects.filter(slug=self.slug)
                if len(existing) == 0:
                    break
                self.slug = "%s-%s" % (slug, count + 1)
                count += 1

        try:
            self.update_learn_api()
        except:
            log.error('Could not update course info in the learn API')
        
        super(Project, self).save()


    def set_duration(self, value):
        """Sets (without saving) duration in hours and minutes given a decimal value.

        e.g., a decimal value of 10.3 equals 10 hours and 18 minutes."""
        value = value or 0
        hours = int(value)
        minutes = int(60 * (value - hours))
        self.duration_hours = hours
        self.duration_minutes = minutes

    def get_duration(self):
        """Gets closest decimal value that represents the current duration.

        e.g., a duration of 10 hours and 18 minutes corresponds to the decimal value 10.3
        """
        return round(self.duration_hours + (self.duration_minutes / 60.0), 1)

    def get_image_url(self):
        missing = settings.STATIC_URL + 'images/project-missing.png'
        image_path = self.image.url if self.image else missing
        return image_path

    def get_learn_api_data(self):
        """ return data used for learn API """
        course_url = reverse('projects_show', kwargs={'slug': self.slug})
        learn_api_data = {
            "course_url": course_url,
            "title": self.name,
            "description": self.short_description,
            "data_url": "",
            "language": self.language,
            "thumbnail_url": self.get_image_url(),
            "tags": self.tags.all().values_list('name', flat=True)
        }
        return learn_api_data

    def send_creation_notification(self):
        """Send notification when a new project is created."""
        subject_template = 'projects/emails/project_created_subject.txt'
        body_template = 'projects/emails/project_created.txt'
        context = {
            'project': self,
            'domain': Site.objects.get_current().domain,
        }
        profiles = [recipient.user for recipient in self.organizers()]
        send_notifications_i18n(profiles, subject_template, body_template,
            context, notification_category='course-created'
        )
        if not self.test:
            admin_subject = render_to_string(
                "projects/emails/admin_project_created_subject.txt",
                context).strip()
            admin_body = render_to_string(
                "projects/emails/admin_project_created.txt", context).strip()
            # TODO send using notifications and get email addresses from group, not settings
            for admin_email in settings.ADMIN_PROJECT_CREATE_EMAIL:
                send_mail(admin_subject, admin_body, admin_email,
                    [admin_email], fail_silently=True)

    def accepted_school(self):
        # Used previously when schools had to decline groups.
        return self.school

    def check_tasks_completion(self, user):
        total_count = self.pages.filter(listed=True,
            deleted=False).count()
        completed_count = PerUserTaskCompletion.objects.filter(
            page__project=self, page__deleted=False,
            unchecked_on__isnull=True, user=user).count()
        if total_count == completed_count:
            for badge in self.completion_badges.all():
                badge.award_to(user)

    def completed_tasks_users(self):
        custom_query = """
SELECT
    `relationships_relationship`.`id`,
    `relationships_relationship`.`source_id`,
    `relationships_relationship`.`target_user_id`,
    `relationships_relationship`.`target_project_id`,
    `relationships_relationship`.`created_on`,
    `relationships_relationship`.`deleted`
FROM
    `relationships_relationship`
INNER JOIN
    `users_userprofile` ON (`relationships_relationship`.`source_id` = `users_userprofile`.`id`)
INNER JOIN
    `projects_perusertaskcompletion` ON  (`relationships_relationship`.`source_id` = `projects_perusertaskcompletion`.`user_id`)
INNER JOIN
    `content_page` U1 ON (`projects_perusertaskcompletion`.`page_id` = U1.`id`)
WHERE
    `projects_perusertaskcompletion`.`unchecked_on` IS NULL
    AND U1.`project_id` = {project_id}
    AND U1.`deleted` = False
    AND `users_userprofile`.`deleted` = False
    AND `relationships_relationship`.`target_project_id` = {project_id}
GROUP BY
    `projects_perusertaskcompletion`.`user_id`, `projects_perusertaskcompletion`.`user_id`
HAVING
    COUNT(`projects_perusertaskcompletion`.`page_id`) = {task_count}
LIMIT 56;"""
        total_count = self.pages.filter(listed=True,
            deleted=False).count()
        #completed_stats = PerUserTaskCompletion.objects.filter(
        #    page__project=self, page__deleted=False,
        #    unchecked_on__isnull=True).values(
        #    'user').annotate(completed_count=Count('page')).filter(
        #    completed_count=total_count)
        #usernames = completed_stats.values_list(
        #    'user', flat=True)
        #return Relationship.objects.filter(source__in=usernames,
        #    target_project=self, source__deleted=False)
        return Relationship.objects.raw(custom_query.format(project_id=self.id, task_count=total_count))

    def get_badges(self):
        from badges.models import Badge
        return Badge.objects.filter(
            Q(groups=self.id) | Q(all_groups=True)).distinct()

    def get_submission_enabled_badges(self):
        from badges.models import Logic
        return self.get_badges().exclude(
            logic__submission_style=Logic.NO_SUBMISSIONS)

    def get_badges_peers_can_give(self):
        from badges.models import Logic, Badge
        return self.get_badges().filter(
            logic__min_votes=1, logic__min_avg_rating=0).exclude(
            logic__submission_style=Logic.SUBMISSION_REQUIRED)

    def get_upon_completion_badges(self, user):
        from badges.models import Badge, Award
        if user.is_authenticated():
            profile = user.get_profile()
            awarded_badges = Award.objects.filter(
                user=profile).values('badge_id')
            self_completion_badges = self.completion_badges.all()
            upon_completion_badges = []
            for badge in self_completion_badges:
                missing_prerequisites = badge.prerequisites.exclude(
                    id__in=awarded_badges).exclude(
                    id__in=self_completion_badges.values('id'))
                if not missing_prerequisites.exists():
                    upon_completion_badges.append(badge.id)
            return Badge.objects.filter(id__in=upon_completion_badges)
        else:
            return Badge.objects.none()

    def get_awarded_badges(self, user, exclude_completion_badges=False):
        from badges.models import Badge, Award
        if user.is_authenticated():
            profile = user.get_profile()
            project_badges = self.get_badges()
            if exclude_completion_badges:
                completion_badges = self.completion_badges.all()
                project_badges = project_badges.exclude(
                    id__in=completion_badges.values('id'))
            awarded_badges = Award.objects.filter(
                user=profile).values('badge_id')
            return project_badges.filter(
                id__in=awarded_badges)
        else:
            return Badge.objects.none()

    def get_badges_in_progress(self, user):
        from badges.models import Badge, Award, Submission
        if user.is_authenticated():
            profile = user.get_profile()
            awarded_badges = Award.objects.filter(
                user=profile).values('badge_id')
            attempted_badges = Submission.objects.filter(
                author=profile, pending=True).values('badge_id')
            return self.badges.filter(
                id__in=attempted_badges).exclude(
                id__in=awarded_badges)
        else:
            return Badge.objects.none()

    def get_non_attempted_badges(self, user):
        from badges.models import Badge, Award, Submission
        if user.is_authenticated():
            profile = user.get_profile()
            awarded_badges = Award.objects.filter(
                user=profile).values('badge_id')
            attempted_badges = Submission.objects.filter(
                author=profile).values('badge_id')
            project_badges = self.get_submission_enabled_badges()
            # Excluding both awarded and attempted badges
            # In case honorary award do not rely on submissions.
            return project_badges.exclude(
                id__in=attempted_badges).exclude(
                id__in=awarded_badges)
        else:
            return Badge.objects.none()

    def get_non_started_next_projects(self, user):
        """To be displayed in the Join Next Challenges section."""
        if user.is_authenticated():
            profile = user.get_profile()
            joined = Participation.objects.filter(
                user=profile).values('project_id')
            return self.next_projects.exclude(
                id__in=joined)
        else:
            return Project.objects.none()
   
    @staticmethod
    def filter_activities(activities):
        from statuses.models import Status
        content_types = [
            ContentType.objects.get_for_model(Page),
            ContentType.objects.get_for_model(PageComment),
            ContentType.objects.get_for_model(Status),
            ContentType.objects.get_for_model(Project),
        ]
        return activities.filter(target_content_type__in=content_types)

    @staticmethod
    def filter_learning_activities(activities):
        pages_ct = ContentType.objects.get_for_model(Page)
        comments_ct = ContentType.objects.get_for_model(PageComment)
        return activities.filter(
            target_content_type__in=[pages_ct, comments_ct])

register_filter('default', Project.filter_activities)
register_filter('learning', Project.filter_learning_activities)


class Participation(ModelBase):
    user = models.ForeignKey('users.UserProfile',
        related_name='participations')
    project = models.ForeignKey('projects.Project',
        related_name='participations')
    organizing = models.BooleanField(default=False)
    adopter = models.BooleanField(default=False)
    joined_on = models.DateTimeField(
        auto_now_add=True, default=datetime.datetime.now)
    left_on = models.DateTimeField(blank=True, null=True)
    # Notification Preferences.
    no_organizers_wall_updates = models.BooleanField(default=False)
    no_organizers_content_updates = models.BooleanField(default=False)
    no_participants_wall_updates = models.BooleanField(default=False)
    no_participants_content_updates = models.BooleanField(default=False)


class PerUserTaskCompletion(ModelBase):
    user = models.ForeignKey('users.UserProfile',
        related_name='peruser_task_completion')
    page = models.ForeignKey('content.Page',
        related_name='peruser_task_completion')
    checked_on = models.DateTimeField(auto_now_add=True,
        default=datetime.datetime.now)
    unchecked_on = models.DateTimeField(blank=True, null=True)
    url = models.URLField(max_length=1023, blank=True, null=True)


###########
# Signals #
###########

def check_tasks_completion(sender, **kwargs):
    instance = kwargs.get('instance', None)
    if isinstance(instance, PerUserTaskCompletion):
        project = instance.page.project
        user = instance.user
        project.check_tasks_completion(user)


post_save.connect(check_tasks_completion, sender=PerUserTaskCompletion,
    dispatch_uid='projects_check_tasks_completion')
