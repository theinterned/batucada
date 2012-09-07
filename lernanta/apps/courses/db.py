from django.db import models

from drumbeat.models import ModelBase

class Course(ModelBase):
    
    title = models.CharField(max_length=255)

    short_title = models.CharField(max_length=20)

    plug = models.CharField(max_length=1000)


class CourseContent(ModelBase):

    course = models.ForeignKey('courses.Course', related_name='content')
    content = models.ForeignKey('content.Page')
    index = models.PositiveIntegerField()
