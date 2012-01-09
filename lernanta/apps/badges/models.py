import datetime

from django.db import models
from django.conf import settings
from django.db.models import Avg
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from django.db.models.signals import post_save

from drumbeat import storage
from drumbeat.utils import get_partition_id, safe_filename, MultiQuerySet
from drumbeat.models import ModelBase
from richtext.models import RichTextField


def determine_upload_path(instance, filename):
    chunk_size = 1000  # max files per directory
    return "images/badges/%(partition)d/%(filename)s" % {
        'partition': get_partition_id(instance.pk, chunk_size),
        'filename': safe_filename(filename),
    }


def get_awarded_badges(user):
    from pilot import get_awarded_badges as get_pilot_badges
    return get_pilot_badges(user)


class Badge(ModelBase):
    """Representation of a Badge"""
    name = models.CharField(max_length=225, blank=False)
    slug = models.SlugField(unique=True, max_length=110)
    description = models.CharField(max_length=225, blank=False)
    requirements = RichTextField(blank=True, null=True)
    image = models.ImageField(
        upload_to=determine_upload_path, default='', blank=True, null=True,
        storage=storage.ImageStorage())
    prerequisites = models.ManyToManyField('self', symmetrical=False,
        blank=True, null=True)
    unique = models.BooleanField(
        help_text=_('If can only be awarded to the user once.'),
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

    assessment_type = models.CharField(max_length=30,
        choices=ASSESSMENT_TYPE_CHOICES,
        default=SELF, null=True, blank=False)

    COMPLETION = 'completion/aggregate'
    SKILL = 'skill'
    COMMUNITY = 'peer-to-peer/community'
    STEALTH = 'stealth'
    OTHER = 'other'

    BADGE_TYPE_CHOICES = (
        (COMPLETION, _('Completion/aggregate badge -- awarded by self '\
            'assessments')),
        (SKILL, _('Skill badge -- badges that are skill based and assessed '\
            'by peers with related logic')),
        (COMMUNITY, _('Peer-to-peer/community badge -- badges granted by '\
            'peers')),
        (STEALTH, _('Stealth badge -- system awarded badges')),
        (OTHER, _('Other badges -- badges like course organizer or those '\
            'staff issued'))
    )

    badge_type = models.CharField(max_length=30, choices=BADGE_TYPE_CHOICES,
        default=COMPLETION, null=True, blank=False)

    rubrics = models.ManyToManyField('badges.Rubric', related_name='badges',
        null=True, blank=True)
    logic = models.ForeignKey('badges.Logic', related_name='badges',
        null=True, blank=True,
        help_text=_('If no logic is chosen, no logic required. '\
        ' Example: self-assessment badges.'))

    groups = models.ManyToManyField('projects.Project', related_name='badges',
        null=True, blank=True)

    creator = models.ForeignKey('users.UserProfile', related_name='badges',
        blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True, blank=False)

    def __unicode__(self):
        return "%s %s" % (self.name, _('Badge'))

    @models.permalink
    def get_absolute_url(self):
        return ('badges_show', (), {
            'slug': self.slug,
        })

    def get_image_url(self):
        # TODO: using project's default image until a default badge
        # image is added.
        missing = settings.MEDIA_URL + 'images/missing-badge.png'
        image_path = self.image.url if self.image else missing
        return image_path

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
        """Check if the user eligible for the badge.

        If some prerequisite badges have not been
        awarded returns False."""
        awarded_badges = Award.objects.filter(
            user=user).values('badge_id')
        return not self.prerequisites.exclude(
            id__in=awarded_badges).exists()

    def is_awarded_to(self, user):
        """Does the user have the badge?"""
        return Award.objects.filter(user=user, badge=self).count() > 0

    def award_to(self, user):
        """Award the badge to the user.

        Returns None if no badge is awarded."""
        if not self.is_eligible(user):
            # If the user is not eligible the badge
            # is not awarded.
            return None

        # If logic restrictions are not meet the badge is not awarded.
        if self.logic and not self.logic.is_eligible(self, user):
            return None

        if self.unique:
            # Do not award the badge if the user can not have the badge
            # more than once and it was already awarded.
            award, created = Award.objects.get_or_create(user=user,
                badge=self)
            return award if created else None

        return Award.objects.create(user=user, badge=self)

    def get_pending_submissions(self):
        """Submissions of users who haven't received the award yet"""
        all_submissions = Submission.objects.filter(badge=self)
        pending_submissions = []
        for submission in all_submissions:
            if not self.is_awarded_to(submission.author):
                pending_submissions.append(submission)
        return pending_submissions

    def progress_for(self, user):
        """Progress for a user for this badge"""
        progress = Progress.objects.filter(user=user, badge=self)
        if progress:
            progress = progress[0]
        else:
            progress = Progress(user=user, badge=self)
        return progress

    def get_peers(self, profile):
        from projects.models import Participation
        from users.models import UserProfile
        badge_projects = self.groups.values('id')
        user_projects = Participation.objects.filter(
            user=profile).values('project__id')
        peers = Participation.objects.filter(
            project__in=badge_projects).filter(
            project__in=user_projects).values('user__id')
        return UserProfile.objects.filter(deleted=False,
            id__in=peers).exclude(id=profile.id)

    def other_badges_can_apply_for(self):
        badges = Badge.objects.exclude(
            id=self.id).filter(badge_type=Badge.SKILL).filter(
            assessment_type=Badge.PEER)
        badge_groups = self.groups.values('id')
        related_badges = badges.filter(
            groups__in=badge_groups).distinct()
        non_related_badges = badges.exclude(
            groups__in=badge_groups).distinct()
        return MultiQuerySet(related_badges, non_related_badges)

class Rubric(ModelBase):
    """Criteria for which a badge application is judged"""
    question = models.CharField(max_length=200)

    def __unicode__(self):
        return self.question


class Logic(ModelBase):
    """Representation of the logic behind awarding a badge"""
    name = models.CharField(max_length=30)
    min_votes = models.PositiveIntegerField(
        help_text=_('Minimum number of votes.'),
        default=0)
    min_avg_rating = models.PositiveIntegerField(
        help_text=_('Minimum average rating.'),
        default=0)

    def __unicode__(self):
        msg = _('%(min_votes)s peers -- by an average rating of %(min_avg)s -- ')
        return msg % {'min_votes': self.min_votes, 'min_avg': self.min_avg_rating}

    def is_eligible(self, badge, user):
        progress = badge.progress_for(user)
        if self.min_votes and self.min_votes > progress.current_votes:
            return False
        min_avg = self.min_avg_rating
        current_avg = progress.current_avg_rating
        if min_avg and min_avg > current_avg:
            return False
        return True


class Progress(ModelBase):
    """Progress of a person to getting awarded a badge"""
    badge = models.ForeignKey('badges.Badge', related_name="progresses")
    current_votes = models.PositiveIntegerField(default=0,
        help_text=_('Current number of votes'))
    current_rating = models.FloatField(default=0,
        help_text=_('Current total rating'))
    user = models.ForeignKey('users.UserProfile')
    updated_on = models.DateTimeField(
        help_text=_('Last time this person received a qualified rating'),
        auto_now_add=True, default=datetime.datetime.now)
    created_on = models.DateTimeField(
        help_text=_('First time this person received a qualified rating'),
        auto_now_add=True, default=datetime.datetime.now)

    @property
    def current_avg_rating(self):
        if self.current_votes == 0:
            return 0
        return self.current_rating / self.current_votes

    def __unicode__(self):
        return _('%(user)s progress for %(badge)s') % {
            'user': self.user, 'badge': self.badge}

    def update_progress(self, assessment):
        """Progress should be updated only once after the assessment
        and all its ratings are saved, and the assessment final_rating
        updated."""
        badge = assessment.badge
        self.current_votes += 1
        self.current_rating += assessment.final_rating
        self.update_date = datetime.datetime.now()
        self.save()
        # Try to award badge to user
        badge.award_to(assessment.assessed)


class Submission(ModelBase):
    """Application for a badge"""
    # TODO Refactor this and PageComment and Assessment?
    # to extend off same base
    url = models.URLField(max_length=1023)
    content = RichTextField(config_name='rich', blank=False)
    author = models.ForeignKey('users.UserProfile', related_name='submissions')
    badge = models.ForeignKey('badges.Badge', related_name="submissions")
    created_on = models.DateTimeField(auto_now_add=True,
        default=datetime.datetime.now)

    def __unicode__(self):
        return _('%(author)s\'s application for %(badge)s') % {
            'author': self.author, 'badge': self.badge}

    @models.permalink
    def get_absolute_url(self):
        return ('submission_show', (), {
            'slug': self.badge.slug,
            'submission_id': self.id,
        })


class Assessment(ModelBase):
    """Assessment for a badge"""
    final_rating = models.FloatField(default=0)
    weight = models.FloatField(default=1,
        help_text=_("Allows to give more or less weight to the assessor's vote."))
    assessor = models.ForeignKey('users.UserProfile',
        related_name='assessments')
    assessed = models.ForeignKey('users.UserProfile',
        related_name='badge_assessments')
    comment = RichTextField(config_name='rich', blank=False)
    badge = models.ForeignKey('badges.Badge', related_name="assessments")
    created_on = models.DateTimeField(auto_now_add=True,
        default=datetime.datetime.now)
    submission = models.ForeignKey('badges.Submission',
        related_name="assessments", null=True, blank=True,
        help_text=_('If submission is blank, this is a '\
        'peer awarded assessment or superuser granted'))
    ready = models.BooleanField(default=False,
        help_text=_("If all rubric ratings were provided."))

    def __unicode__(self):
        return _('%(assessor)s for %(assessed)s for %(badge)s') % {
            'assessor': self.assessor, 'assessed': self.assessed,
            'badge': self.badge}

    @models.permalink
    def get_absolute_url(self):
        return ('assessment_show', (), {
            'slug': self.badge.slug,
            'assessment_id': self.id,
        })

    def final_rating_as_percentage(self):
        """Return the final rating as a percentage for
        styling of assessment view. Max number of ratings
        is 4"""
        return (self.final_rating / 4.0) * 100

    def get_final_rating_display(self):
        rating_position = int(round(self.final_rating)) - 1
        # Guarantee rating_position does not go above or below
        # the boundaries.
        if rating_position < 0:
            rating_position = 0
        max_index = len(Rating.RATING_CHOICES) - 1
        if rating_position > max_index:
            rating_position = max_index
        return Rating.RATING_CHOICES[rating_position][1]

    def update_final_rating(self):
        """Used on Rating save signal to update the final
        rating for the assessment"""
        ratings = Rating.objects.filter(assessment=self)
        self.final_rating = ratings.aggregate(
            final_rating=Avg('score'))['final_rating']
        if ratings.count() == self.badge.rubrics.count():
            self.ready = True
        self.save()

    @classmethod
    def compute_average_rating(cls, assessments):
        ratings_sum = 0
        weights_sum = 0
        for assessment in assessments:
            ratings_sum += assessment.final_rating
            weights_sum += assessment.weight
        return ratings_sum / weights_sum if weights_sum > 0 else 0 


class Rating(ModelBase):
    """Assessor's rating for the assessment's rubric(s)"""

    NEVER = 1
    SOMETIMES = 2
    MOST_OF_THE_TIME = 3
    ALWAYS = 4

    RATING_CHOICES = (
        (NEVER, _('Never')),
        (SOMETIMES, _('Sometimes')),
        (MOST_OF_THE_TIME, _('Most of the time')),
        (ALWAYS, _('Always'))
    )

    assessment = models.ForeignKey('badges.Assessment', related_name='ratings')
    score = models.PositiveIntegerField(default=1, choices=RATING_CHOICES)
    rubric = models.ForeignKey('badges.Rubric', related_name='ratings')
    created_on = models.DateTimeField(auto_now_add=True,
        default=datetime.datetime.now)

    def __unicode__(self):
        return _('%(score)s for %(rubric)s') % {
            'score': self.score,
            'rubric': self.rubric
        }

    def score_as_percentage(self):
        """Return the score as a percentage for
        styling of assessment view. Max number of ratings
        is 4"""
        return (self.score / 4.0) * 100


class Award(ModelBase):
    """Representation of a badge a user has received"""
    user = models.ForeignKey('users.UserProfile')
    badge = models.ForeignKey('badges.Badge', related_name="awards")
    awarded_on = models.DateTimeField(auto_now_add=True, blank=False)

    def __unicode__(self):
        return _('%(user)s - %(badge)s') % {'user': self.user,
            'badge': self.badge}

    @models.permalink
    def get_absolute_url(self):
        # All the awards of the same badge to the same user
        # share one awards page.
        return ('user_awards_show', (), {
            'slug': self.badge.slug,
            'username': self.user.username,
        })


###########
# Signals #
###########

def post_rating_save(sender, **kwargs):
    instance = kwargs.get('instance', None)
    created = kwargs.get('created', False)
    if created and isinstance(instance, Rating):
        assessment = instance.assessment
        badge = assessment.badge
        assessment.update_final_rating()
        if assessment.ready:
            progress = badge.progress_for(assessment.assessed)
            progress.update_progress(assessment)

post_save.connect(post_rating_save, sender=Rating,
    dispatch_uid='badges_post_rating_save')


def post_assessment_save(sender, **kwargs):
    instance = kwargs.get('instance', None)
    created = kwargs.get('created', False)
    if created and isinstance(instance, Assessment):
        badge = instance.badge
        if instance.ready:
            progress = badge.progress_for(instance.assessed)
            progress.update_progress(instance)

post_save.connect(post_assessment_save, sender=Assessment,
    dispatch_uid='badges_post_assessment_save')
