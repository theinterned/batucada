from djanog.db.models import Model

class Course(Model):
    title = models.CharField()
    url = models.CharField()
    description = models.CharField()
    tags = models.ListField() #wishfull thinking
    data_url = models.CharField()
