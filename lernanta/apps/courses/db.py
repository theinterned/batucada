from django.db import models

from drumbeat.models import ModelBase

class Course(ModelBase):

    title = models.CharField(max_length=255)
    short_title = models.CharField(max_length=20)
    plug = models.CharField(max_length=1000)
    creation_date = models.DateTimeField(auto_now_add=True)
    draft = models.BooleanField(default=True)
    archived = models.BooleanField(default=False)


class CourseContent(ModelBase):

    course = models.ForeignKey(Course, related_name='content')
    content_uri = models.CharField(max_length=256) 
    index = models.PositiveIntegerField()


class Cohort(ModelBase):

    OPEN = "OPEN"
    MODERATED = "MODERATED"
    CLOSED = "CLOSED"
    SIGNUP_MODELS = (
        (OPEN, "Anyone can sign up"),
        (MODERATED, "Signups are moderated"),
        (CLOSED, "Signups are closed"),
    )

    ROLLING = "ROLLING"
    FIXED = "FIXED"
    TERM_CHOICES = (
        (ROLLING, "Rolling"),
        (FIXED, "Fixed"),
    )

    course = models.ForeignKey(Course, related_name="cohort_set")
    term = models.CharField(max_length=32, choices=TERM_CHOICES)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    signup = models.CharField(max_length=32, choices=SIGNUP_MODELS)


class CohortSignup(ModelBase):

    LEARNER = "LEARNER"
    ORGANIZER = "ORGANIZER"
    SIGNUP_ROLE_CHOICES = (
        (LEARNER, "Learner"),
        (ORGANIZER, "Organizer"),
    )

    cohort = models.ForeignKey(Cohort, related_name="signup_set")
    user_uri = models.CharField(max_length=256)
    role = models.CharField(max_length=10, choices=SIGNUP_ROLE_CHOICES)
    signup_date = models.DateTimeField(auto_now_add=True)
    leave_date = models.DateTimeField(blank=True, null=True)


class CohortComment(ModelBase):

    cohort = models.ForeignKey(Cohort, related_name="comment_set")
    comment_uri = models.CharField(max_length=256)
    reference_uri = models.CharField(max_length=256)

