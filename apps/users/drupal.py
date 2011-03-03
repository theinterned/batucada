from django.db import models


DRUPAL_DB = 'drupal_users'


def get_user(username):
    try:
        if '@' in username:
            return Users.objects.using(DRUPAL_DB).get(mail=username)
        else:
            return Users.objects.using(DRUPAL_DB).get(name=username)
    except Users.DoesNotExist:
        return None


class Users(models.Model):

    uid = models.IntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=180)
    password = models.CharField(max_length=96, db_column='pass')
    mail = models.CharField(max_length=192, blank=True)
    mode = models.IntegerField()
    sort = models.IntegerField(null=True, blank=True)
    threshold = models.IntegerField(null=True, blank=True)
    theme = models.CharField(max_length=765)
    signature = models.CharField(max_length=765)
    signature_format = models.IntegerField()
    created = models.IntegerField()
    access = models.IntegerField()
    login = models.IntegerField()
    status = models.IntegerField()
    timezone = models.CharField(max_length=24, blank=True)
    language = models.CharField(max_length=36)
    picture = models.CharField(max_length=765)
    init = models.CharField(max_length=192, blank=True)
    data = models.TextField(blank=True)
    timezone_name = models.CharField(max_length=150)

    class Meta:
        db_table = u'users'

