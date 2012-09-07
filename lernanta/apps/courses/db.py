from django.db import models

from drumbeat.models import ModelBase

class Course(ModelBase):
    
    title = models.CharField(max_length=255)
    short_title = models.CharField(max_length=20)
    plug = models.CharField(max_length=1000)


class CourseContent(ModelBase):

    course = models.ForeignKey('courses.Course', related_name='content')
    content_uri = models.CharField(max_length=256) #use URI because content should be in a separate module
    index = models.PositiveIntegerField()


#TODO separate from other course stuff
class Content(ModelBase):

    latest = models.ForeignKey('courses.ContentVersion', related_name='+', null=True, blank=True)


#TODO separate from other course stuff
class ContentVersion(ModelBase):

    container = models.ForeignKey(Content, related_name='versions')
    title = models.CharField(max_length = 100)
    content = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    comment = models.CharField(max_length = 100)
    #TODO author
