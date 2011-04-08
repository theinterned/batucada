import os
import logging
import datetime
import bleach

from django.core.cache import cache
from django.conf import settings
from django.contrib import admin
from django.db import models
from django.db.models import Count, Q 
from django.db.models.signals import pre_save, post_save, post_delete 
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
from django.contrib.sites.models import Site

from drumbeat import storage
from drumbeat.utils import get_partition_id, safe_filename
from users.tasks import SendUserEmail
from drumbeat.models import ModelBase
from statuses.models import Status
from relationships.models import Relationship
from content.models import Page
from activity.models import Activity

from projects.tasks import ThumbnailGenerator

import caching.base
 
log = logging.getLogger(__name__)


def determine_image_upload_path(instance, filename):
    return "images/projects/%(partition)d/%(filename)s" % {
        'partition': get_partition_id(instance.pk),
        'filename': safe_filename(filename),
    }


def determine_media_upload_path(instance, filename):
    if instance.is_video():
        fmt = "videos/projects/%(partition)d/%(filename)s"
    else:
        fmt = "images/projects/%(partition)d/%(filename)s"
    return fmt % {
        'partition': get_partition_id(instance.project.pk),
        'filename': safe_filename(filename),
    }


class ProjectManager(caching.base.CachingManager):
    def get_popular(self, limit=0):
        popular = cache.get('projects_popular')
        if not popular:
            rels = Relationship.objects.values('target_project').annotate(
                Count('id')).exclude(target_project__isnull=True).filter(
                target_project__featured=False).order_by('-id__count')[:limit]
            popular = [r['target_project'] for r in rels]
            cache.set('projects_popular', popular, 3000)
        return Project.objects.filter(id__in=popular)


class Project(ModelBase):
    """Placeholder model for projects."""
    object_type = 'http://drumbeat.org/activity/schema/1.0/project'
    generalized_object_type = 'http://activitystrea.ms/schema/1.0/group'

    name = models.CharField(max_length=100)
    short_description = models.CharField(max_length=125)
    long_description = models.TextField()

    detailed_description = models.ForeignKey('content.Page', related_name='desc_project', null=True, blank=True)
    sign_up = models.ForeignKey('content.Page', related_name='sign_up_project', null=True, blank=True)

    image = models.ImageField(upload_to=determine_image_upload_path, null=True,
                              storage=storage.ImageStorage(), blank=True)

    slug = models.SlugField(unique=True)
    created_by = models.ForeignKey('users.UserProfile',
                                   related_name='projects')
    featured = models.BooleanField()
    created_on = models.DateTimeField(
        auto_now_add=True, default=datetime.datetime.now)

    PRIVATE_DRAFT, PUBLIC_DRAFT, READY = (1, 2, 3)
    preparation_status_choices = ((PRIVATE_DRAFT, _('Private Draft')),
        (PUBLIC_DRAFT, _('Public Draft')),
        (READY, _('Ready')))
    preparation_status = models.PositiveSmallIntegerField(_('Preparation Status'),
        choices=preparation_status_choices, default=PRIVATE_DRAFT)

    objects = ProjectManager()

    class Meta:
        verbose_name = _('course')

    def followers(self):
        """Return a list of users following this project."""
        relationships = Relationship.objects.select_related(
            'source', 'created_by').filter(target_project=self)
        return [rel.source for rel in relationships]

    def non_participant_followers(self):
        from users.models import UserProfile
        followers_ids = Relationship.objects.select_related(
            'source', 'created_by').filter(target_project=self).values('source_id')
        followers = UserProfile.objects.filter(id__in=followers_ids)
        non_participants = followers.exclude(pk=self.created_by.pk)
        non_participants = non_participants.exclude(id__in=self.participants().values('user_id'))
        return non_participants

    def participants(self):
        """Return a list of users participating in this project."""
        return Participation.objects.filter(project=self, left_on__isnull=True)

    def activities(self):
        activities = Activity.objects.filter(
            Q(project=self) | Q(target_project=self),
        ).exclude(
            verb='http://activitystrea.ms/schema/1.0/follow'
        ).order_by('-created_on')
        return activities

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('projects_show', (), {
            'slug': self.slug,
        })

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

    def send_update_notification(self, activity):
        """Send update notifications."""
        subject = _('[p2pu-%(slug)s-updates] Course %(name)s was updated') % {
            'slug': self.slug,
            'name': self.name,
            }
        body = render_to_string("projects/emails/course_updated.txt", {
            'activity': activity,
            'project': self,
            'domain': Site.objects.get_current().domain,
        })
        for participation in self.participants():
            if participation.no_updates or activity.actor == participation.user:
                continue
            SendUserEmail.apply_async((participation.user, subject, body))
        if activity.actor != self.created_by:
            SendUserEmail.apply_async((self.created_by, subject, body))

admin.site.register(Project)


class ProjectMedia(ModelBase):
    video_mimetypes = (
        'video/ogg',
        'video/webm',
        'video/mp4',
        'application/ogg',
        'audio/ogg',
    )
    image_mimetypes = (
        'image/png',
        'image/jpg',
        'image/jpeg',
        'image/gif',
    )
    accepted_mimetypes = video_mimetypes + image_mimetypes
    project_file = models.FileField(upload_to=determine_media_upload_path)
    project = models.ForeignKey(Project)
    mime_type = models.CharField(max_length=80, null=True)
    thumbnail = models.ImageField(upload_to=determine_image_upload_path,
                                  null=True, blank=True,
                                  storage=storage.ImageStorage())

    def thumbnail_or_default(self):
        """Return project media's thumbnail or a default."""
        return self.thumbnail or 'images/file-default.png'

    def is_video(self):
        return self.mime_type in self.video_mimetypes


class Participation(ModelBase):
    user = models.ForeignKey('users.UserProfile', related_name='participations')
    project = models.ForeignKey('projects.Project', related_name='participations')
    joined_on = models.DateTimeField(
        auto_now_add=True, default=datetime.datetime.now)
    left_on = models.DateTimeField(blank=True, null=True)
    # The user can configure this preference but the organizer can by pass
    # it with the contact participant form.
    no_updates = models.BooleanField(default=False)
    # Sign-Up answer.
    sign_up = models.OneToOneField('content.PageComment', related_name='participation', null=True, blank=True)

###########
# Signals #
###########

def clean_html(sender, **kwargs):
    instance = kwargs.get('instance', None)
    if isinstance(instance, Project):
        log.debug("Cleaning html.")
        if instance.long_description:
            instance.long_description = bleach.clean(instance.long_description,
                tags=settings.ALLOWED_TAGS, attributes=settings.ALLOWED_ATTRIBUTES,
                styles=settings.ALLOWED_STYLES)

pre_save.connect(clean_html, sender=Project) 

def project_creation_handler(sender, **kwargs):
    project = kwargs.get('instance', None)
    created = kwargs.get('created', False)

    if not created or not isinstance(project, Project):
        log.debug("Nothing to do, returning")
        return

    log.debug("Creating relationship between project creator and project")
    Relationship(source=project.created_by,
                 target_project=project).save()

    try:
        from activity.models import Activity
        act = Activity(actor=project.created_by,
                       verb='http://activitystrea.ms/schema/1.0/post',
                       project=project)
        act.save()
    except ImportError:
        return
post_save.connect(project_creation_handler, sender=Project)


def projectmedia_thumbnail_generator(sender, **kwargs):
    media = kwargs.get('instance', None)
    created = kwargs.get('created', False)

    if not created or not isinstance(media, ProjectMedia):
        return

    ThumbnailGenerator.apply_async(args=(media,))
post_save.connect(projectmedia_thumbnail_generator, sender=ProjectMedia)


def projectmedia_scrubber(sender, **kwargs):
    media = kwargs.get('instance', None)
    if not isinstance(media, ProjectMedia):
        return
    media_root = getattr(settings, 'MEDIA_ROOT', None)
    if not media_root:
        return
    path = lambda f: os.path.join(media_root, f)
    files = []
    if media.project_file:
        files.append(path(media.project_file.name))
    if media.thumbnail:
        files.append(path(media.thumbnail.name))
    for f in files:
        if os.path.exists(f):
            os.unlink(f)
post_delete.connect(projectmedia_scrubber, sender=ProjectMedia)
