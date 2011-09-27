from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify

from drumbeat import storage
from drumbeat.utils import get_partition_id, safe_filename


def determine_upload_path(instance, filename):
    chunk_size = 1000  # max files per directory
    return "images/badges/%(partition)d/%(filename)s" % {
        'partition': get_partition_id(instance.pk, chunk_size),
        'filename': safe_filename(filename),
    }


class Badge(models.Model):
    SELF, PEER, STEALTH = range(1, 4)
    type_choices = ((SELF, _('Self')),
        (PEER, _('Peer')),
        (STEALTH, _('Stealth')))

    name = models.CharField(max_length=225, blank=False)
    slug = models.SlugField(unique=True, max_length=110)
    description = models.CharField(max_length=225, blank=False)
    image = models.ImageField(
        upload_to=determine_upload_path, default='', blank=True, null=True,
        storage=storage.ImageStorage())
    prerequisites = models.ManyToManyField('self', symmetrical=False,
                                            blank=True, null=True)
    unique = models.BooleanField(help_text=_('If can only be awarded to the user once.'), 
                                 default=False)
    SELF = 'self'
    PEER = 'peer'
    STEALTH = 'stealth'

    ASSESSMENT_TYPE_CHOICES = (
        (SELF, _('Self assessment -- able to get the badge without ' \
                        'outside assessment')),
        (PEER, _('Peer assessment -- community or skill badges users ' \
                        'grant each other')),
        (STEALTH, _('Stealth assessment -- badges granted by the system '\
                        'based on supplied logic. Accumulative.'))
    )

    assessment_type = models.CharField(max_length=30, choices=ASSESSMENT_TYPE_CHOICES,
        default=SELF, null=True, blank=False)

    COMPLETION = 'completion/aggregate'
    SKILL = 'skill'
    PEER = 'peer-to-peer/community'
    STEALTH = 'stealth'
    OTHER = 'other'

    BADGE_TYPE_CHOICES = (
        (COMPLETION, _('Completion/aggregate badge -- awarded by self assessments')),
        (SKILL, _('Skill badge -- badges that are skill based and assessed by peers '\
                  'with related logic')),
        (PEER, _('Peer-to-peer/community badge -- badges granted by peers')),
        (STEALTH, _('Stealth badge -- system awarded badges')),
        (OTHER, _('Other badges -- badges like course organizer or those staff issued'))
    )

    badge_type = models.CharField(max_length=30, choices=BADGE_TYPE_CHOICES,
        default=COMPLETION, null=True, blank=False)

    rubrics = models.ManyToManyField('badges.Rubric', related_name='rubrics', 
                                     null=True, blank=True)
    min_organizer_votes = models.PositiveIntegerField(
                            help_text=_('Minimum number of organizer votes required to be awarded.'),
                            default=0)
    min_peer_votes = models.PositiveIntegerField(
                        help_text=_('Minimum number of peer votes required to be awarded.'),
                        default=0)

    groups = models.ManyToManyField('projects.Project', related_name='badges', 
                                    null=True, blank=True)

    creator = models.ForeignKey('users.UserProfile', related_name='badges')
    created_on = models.DateTimeField(auto_now_add=True, blank=False)
    last_update = models.DateTimeField(auto_now_add=True, blank=False)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('badges_show', (), {
            'slug': self.slug,
        })

    def create(self):
        self.save()

    def save(self):
        """Make sure each badge has a unique slug."""
        count = 1
        if not self.slug:
            slug = slugify(self.name)
            self.slug = slug
            while True:
                existing = Badge.objects.filter(slug=self.slug)
                if len(existing) == 0:
                    break
                self.slug = "%s-%s" % (slug, count + 1)
                count += 1
        super(Badge, self).save()

    def is_eligible(self, user):
        """Is the user eligible for the badge?"""
        if user is None:
            return False
        if user == self.creator:
            return False
        for badge in self.prerequisites.all():
            if not badge.is_awarded_to(user):
                return False
        return True

    def is_awarded_to(self, user):
        """Does the user have the badge?"""
        return Award.objects.filter(user=user, badge=self).count() > 0

def get_awarded_badges(user):
    from pilot import get_awarded_badges as get_pilot_badges
    return get_pilot_badges(user)


class Rubric(models.Model):
    question = models.CharField(max_length=200)

    def __unicode__(self):
        return self.question

class Award(models.Model):
    user = models.ForeignKey('users.UserProfile')
    badge = models.ForeignKey('badges.Badge', related_name="awards")

    awarded_on = models.DateTimeField(auto_now_add=True, blank=False)
