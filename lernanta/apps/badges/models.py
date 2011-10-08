import datetime

from django.db import models
from django.conf import settings
from django.db.models import Avg
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from django.db.models.signals import post_save

from drumbeat import storage
from drumbeat.utils import get_partition_id, safe_filename
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


class Badge(models.Model):
    """Representation of a Badge"""
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
    last_update = models.DateTimeField(auto_now_add=True, blank=False)

    def __unicode__(self):
        return "%s %s" % (self.name, _(' badge'))

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

    def award_to(self, user):
        """Award the badge to the user"""
        if not self.is_eligible(user):
            return  # TODO: Throw exception?

        if self.unique and self.is_awarded_to(user):
            # already awarded
            return Award.objects.filter(user=user, badge=self)[0]

        # TODO: check logic
        # if passes, award
        # always awarding for now
        award = Award.objects.create(user=user, badge=self)

        return award

    def get_awards(self):
        return Award.objects.filter(badge=self)

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


class Rubric(models.Model):
    """Criteria for which a badge application is judged"""
    question = models.CharField(max_length=200)

    def __unicode__(self):
        return self.question


class Logic(models.Model):
    """Representation of the logic behind awarding a badge"""
    min_qualified_adopter_votes = models.PositiveIntegerField(
                            help_text=_('Minimum number of qualified votes by organizers, mentors, or adopters required to be awarded'),
                            default=0)
    min_qualified_votes = models.PositiveIntegerField(
                        help_text=_('Minimum number of qualified votes required to be awarded. '\
                                    'Mentor, adopter, or course organizer receives 2 votes per average (min_rating) rating. '\
                                    'Peers receive 1 vote per average (min_rating) rating.'),
                        default=1)
    min_rating = models.PositiveIntegerField(
                        help_text=_('Minimum average rating required to award the badge.'),
                        default=3)

    def __unicode__(self):
        return _('%s adopter votes of %s total votes with at least %s rating') % \
                 (self.min_qualified_adopter_votes, self.min_qualified_votes, self.min_rating)


class Submission(ModelBase):
    """Application for a badge"""
    # TODO Refactor this and PageComment and Assessment? to extend off same base
    url = models.URLField(max_length=1023)
    content = RichTextField(config_name='rich', blank=False)
    author = models.ForeignKey('users.UserProfile', related_name='submissions')
    badge = models.ForeignKey('badges.Badge', related_name="submissions")
    created_on = models.DateTimeField(auto_now_add=True, default=datetime.datetime.now)

    def __unicode__(self):
        return _('%s''s application for %s') % (self.author, self.badge)

    @models.permalink
    def get_absolute_url(self):
        return ('submission_show', (), {
            'submission_id': self.id,
        })


class Assessment(ModelBase):
    """Assessment for a badge"""
    final_rating = models.FloatField(null=True, blank=True, default=0)
    assessor = models.ForeignKey('users.UserProfile', related_name='assessments')
    assessed = models.ForeignKey('users.UserProfile', related_name='badge_assessments')
    comment = RichTextField(config_name='rich', blank=False)
    badge = models.ForeignKey('badges.Badge', related_name="assessments")
    created_on = models.DateTimeField(auto_now_add=True, default=datetime.datetime.now)
    submission = models.ForeignKey('badges.Submission', related_name="assessments",
                                   null=True, blank=True,
                                   help_text=_('If submission is blank, this is a '\
                                               'peer awarded assessment or superuser granted'))
    def final_rating_as_percentage(self):
        """Return the final rating as a percentage for 
        styling of assessment view. Max number of ratings
        is 4"""
        return (self.final_rating/4.0)*100

    def update_final_rating(self):
        """Used on Rating save signal to update the final
        rating for the assessment"""
        ratings = Rating.objects.filter(assessment=self)
        final_rating = ratings.aggregate(final_rating=Avg('score'))['final_rating']
        self.final_rating = final_rating
        self.save()

    def __unicode__(self):
        return _('%s for %s for %s') \
            % (self.assessor, self.assessed, self.badge)


class Rating(ModelBase):
    """Assessor's rating for the assessment's rubric(s)"""

    NEVER = 1
    SOMETIMES = 2
    MOST_OF_THE_TIME = 3
    ALWAYS = 4

    RATING_CHOICES = ((NEVER, 'Never'), 
                      (SOMETIMES, 'Sometimes'),
                      (MOST_OF_THE_TIME, 'Most of the time'),
                      (ALWAYS, 'Always'))

    assessment = models.ForeignKey('badges.Assessment', related_name='ratings')
    score = models.PositiveIntegerField(default=1, choices=RATING_CHOICES)
    rubric = models.ForeignKey('badges.Rubric', related_name='ratings')
    created_on = models.DateTimeField(auto_now_add=True, default=datetime.datetime.now)

    def __unicode__(self):
        return _('%s for %s') % (self.score, self.rubric)

    def score_as_percentage(self):
        """Return the score as a percentage for 
        styling of assessment view. Max number of ratings
        is 4"""
        return (self.score/4.0)*100

class Progress(ModelBase):
    """Progress of a person to getting awarded a badge"""
    badge = models.ForeignKey('badges.Badge', related_name="progresses")
    current_qualified_ratings = models.PositiveIntegerField(default=0,
                                help_text=_('Current number of qualified ratings before next awarding'))
    user = models.ForeignKey('users.UserProfile')
    updated_on = models.DateTimeField(help_text=_('Last time this person received a qualified rating for this badge'),
                                      auto_now_add=True, default=datetime.datetime.now)
    created_on = models.DateTimeField(help_text=_('First time this person received a qualified rating for this badge'),
                                      auto_now_add=True, default=datetime.datetime.now)

    def __unicode__(self):
        return _('%s has %s qualified ratings to get %s') \
            % (self.user, self.current_qualified_ratings, self.badge)


class Award(models.Model):
    """Representation of a badge a user has received"""
    user = models.ForeignKey('users.UserProfile')
    badge = models.ForeignKey('badges.Badge', related_name="awards")
    awarded_on = models.DateTimeField(auto_now_add=True, blank=False)

    def __unicode__(self):
        return _('%s - %s') % (self.user, self.badge)


###########
# Signals #
###########

def update_final_rating(sender, **kwargs):
    instance = kwargs.get('instance', None)
    if isinstance(instance, Rating):
        assessment = instance.assessment
        assessment.update_final_rating()


post_save.connect(update_final_rating, sender=Rating,
    dispatch_uid='badges_update_final_rating')
