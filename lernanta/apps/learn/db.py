from django.db import models

class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    url = models.URLField()
    data_url = models.URLField()
    thumbnail_url = models.URLField()
    language = models.CharField(max_length=10)
    verified = models.BooleanField(default=False)
    date_added = models.DateTimeField(null=True)
    date_checked = models.DateTimeField(null=True)
    date_removed = models.DateTimeField(null=True)


class Lists(models.Model):
    title = models.CharField(max_length=255)
    url = models.URLField()


class CourseListAssignment(models.Model):
    course_list = models.ForeignKey(Lists)
    course = models.ForeignKey(Course)


class CourseTags(models.Model):
    tag = models.CharField(max_length=100)
    course = models.ForeignKey(Course)
    internal = models.BooleanField(default=False)
