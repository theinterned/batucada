import logging
import datetime

from django.core.cache import cache
from django.core.validators import MaxLengthValidator
from django.conf import settings
from django.db import models
from django.db.models import Count, Max
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.contrib.contenttypes.models import ContentType

from taggit.managers import TaggableManager

from drumbeat import storage
from drumbeat.utils import get_partition_id, safe_filename
from drumbeat.models import ModelBase
from relationships.models import Relationship
from activity.models import Activity, RemoteObject, register_filter
from activity.schema import object_types, verbs
from users.tasks import SendUserEmail
from l10n.models import localize_email
from richtext.models import RichTextField
from content.models import Page
from replies.models import PageComment
from tags.models import GeneralTaggedItem

import caching.base

log = logging.getLogger(__name__)


def determine_image_upload_path(instance, filename):
    return "images/projects/%(partition)d/%(filename)s" % {
        'partition': get_partition_id(instance.pk),
        'filename': safe_filename(filename),
    }


class ProjectManager(caching.base.CachingManager):

    def get_popular(self, limit=0, school=None):
        popular = cache.get('projectspopular')
        if not popular:
            rels = Relationship.objects.filter(deleted=False).values(
                'target_project').annotate(Count('id')).exclude(
                target_project__isnull=True).filter(
                target_project__under_development=False,
                target_project__not_listed=False,
                target_project__archived=False).order_by('-id__count')
            if school:
                rels = rels.filter(target_project__school=school).exclude(
                    target_project__id__in=school.declined.values('id'))
            if limit:
                rels = rels[:limit]
            popular = [r['target_project'] for r in rels]
            cache.set('projectspopular', popular, 3000)
        return Project.objects.filter(id__in=popular)

    def get_active(self, limit=0, school=None):
        active = cache.get('projectsactive')
        if not active:
            ct = ContentType.objects.get_for_model(RemoteObject)
            activities = Activity.objects.values('scope_object').annotate(
                Max('created_on')).exclude(scope_object__isnull=True,
                verb=verbs['follow'], target_content_type=ct).filter(
                scope_object__under_development=False,
                scope_object__not_listed=False,
                scope_object__archived=False).order_by('-created_on__max')
            if school:
                activities = activities.filter(
                    scope_object__school=school).exclude(
                    scope_object__id__in=school.declined.values('id'))
            if limit:
                activities = activities[:limit]
            active = [a['scope_object'] for a in activities]
            cache.set('projectsactive', active, 3000)
        return Project.objects.filter(id__in=active)


class Project(ModelBase):
    """Placeholder model for projects."""
    object_type = object_types['group']

    name = models.CharField(max_length=100)

    # Select kind of project (study group, course, or other)
    STUDY_GROUP = 'study group'
    COURSE = 'course'
    OTHER = 'other'
    CATEGORY_CHOICES = (
        (STUDY_GROUP, _('Study Group -- group of people working ' \
                        'collaboratively to acquire and share knowledge.')),
        (COURSE, _('Course -- led by one or more organizers with skills on ' \
                   'a field who direct and help participants during their ' \
                   'learning.')),
        (OTHER, _('Other -- if other, please fill out and describe the ' \
                  'term you will use to categorize it.'))
    )
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES,
        default=STUDY_GROUP, null=True, blank=False)

    tags = TaggableManager(through=GeneralTaggedItem, blank=True)

    other = models.CharField(max_length=30, blank=True, null=True)
    other_description = models.CharField(max_length=150, blank=True, null=True)

    short_description = models.CharField(max_length=150)
    long_description = RichTextField(validators=[MaxLengthValidator(700)])

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    school = models.ForeignKey('schools.School', related_name='projects',
        null=True, blank=True)

    detailed_description = models.ForeignKey('content.Page',
        related_name='desc_project', null=True, blank=True)

    image = models.ImageField(upload_to=determine_image_upload_path, null=True,
                              storage=storage.ImageStorage(), blank=True)

    slug = models.SlugField(unique=True, max_length=110)
    featured = models.BooleanField(default=False)
    created_on = models.DateTimeField(
        auto_now_add=True, default=datetime.datetime.now)

    under_development = models.BooleanField(default=True)
    not_listed = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)

    clone_of = models.ForeignKey('projects.Project', blank=True, null=True,
        related_name='derivated_projects')

    imported_from = models.CharField(max_length=150, blank=True, null=True)

    objects = ProjectManager()

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
        if self.category == Project.OTHER:
            return self.other.lower()
        else:
            return self.category.lower()

    def followers(self):
        return Relationship.objects.filter(deleted=False,
            target_project=self, source__deleted=False)

    def non_participant_followers(self):
        return self.followers().exclude(
            source__id__in=self.participants().values('user_id'))

    def participants(self):
        """Return a list of users participating in this project."""
        return Participation.objects.filter(project=self,
            left_on__isnull=True, user__deleted=False)

    def non_organizer_participants(self):
        return self.participants().filter(organizing=False)

    def organizers(self):
        return self.participants().filter(organizing=True)

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

    def activities(self):
        return Activity.objects.filter(deleted=False,
            scope_object=self).order_by('-created_on')

    def create(self):
        self.save()
        self.send_creation_notification()

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
        super(Project, self).save()

    def get_image_url(self):
        missing = settings.MEDIA_URL + 'images/project-missing.png'
        image_path = self.image.url if self.image else missing
        return image_path

    def send_creation_notification(self):
        """Send notification when a new project is created."""
        context = {
            'project': self,
            'domain': Site.objects.get_current().domain,
        }
        subjects, bodies = localize_email(
            'projects/emails/project_created_subject.txt',
            'projects/emails/project_created.txt', context)
        for organizer in self.organizers():
            if not organizer.no_updates:
                SendUserEmail.apply_async(
                        (organizer.user, subjects, bodies))

        admin_subject = render_to_string(
            "projects/emails/admin_project_created_subject.txt",
            context).strip()
        admin_body = render_to_string(
            "projects/emails/admin_project_created.txt", context).strip()
        for admin_email in settings.ADMIN_PROJECT_CREATE_EMAIL:
            send_mail(admin_subject, admin_body, admin_email,
                [admin_email], fail_silently=True)

    def accepted_school(self):
        school = self.school
        if school and school.declined.filter(id=self.id).exists():
            school = None
        return school

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
    joined_on = models.DateTimeField(
        auto_now_add=True, default=datetime.datetime.now)
    left_on = models.DateTimeField(blank=True, null=True)
    # The user can configure this preference but the organizer can by pass
    # it with the contact participant form.
    no_wall_updates = models.BooleanField(default=False)
    # for new pages or comments.
    no_updates = models.BooleanField(default=False)
