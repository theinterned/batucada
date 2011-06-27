import logging

from django.db import models
from django.conf import settings
from django.contrib.auth.models import check_password as django_check_password
from django.contrib.auth.models import get_hexdigest as django_get_hexdigest
from django.contrib.auth.models import User
from django.db.utils import IntegrityError


log = logging.getLogger(__name__)


DRUPAL_DB = 'drupal_db'
GOOGLE_OPENID = 'www.google.com/accounts/o8/id'
PREFIXES = ('', 'https://', 'http://',)
SUFIXES = ('', '/',)


def get_user(username):
    if not DRUPAL_DB in settings.DATABASES:
        return None
    try:
        if '@' in username:
            return Users.objects.using(DRUPAL_DB).get(mail=username)
        else:
            return Users.objects.using(DRUPAL_DB).get(name=username)
    except Users.DoesNotExist:
        return None
    except TypeError:
        # TypeError: 'DoesNotExist' object is not callable
        return None


def normalize(url):
    normalized = url
    for prefix in PREFIXES[1:]:
        if normalized.startswith(prefix):
            normalized = normalized[len(prefix):]
    for sufix in SUFIXES[1:]:
        if normalized.endswith(sufix):
            normalized = normalized[:-len(sufix)]
    return normalized


def get_openid_user(identity_url):
    if not DRUPAL_DB in settings.DATABASES:
        return None
    if GOOGLE_OPENID in identity_url:
        return None
    urls = [identity_url]
    normalized = normalize(identity_url)
    for prefix in PREFIXES:
        for sufix in SUFIXES:
            urls.append(prefix + normalized + sufix)
    log.debug('Searching for similar openid urls: %s' % urls)
    try:
        authmap = Authmap.objects.using(DRUPAL_DB).get(authname__in=urls)
        return Users.objects.using(DRUPAL_DB).get(uid=authmap.uid)
    except Authmap.DoesNotExist, Users.DoesNotExist:
        return None


def check_password(drupal_user, password):
    if '$' not in drupal_user.password:
        encripted_password = django_get_hexdigest('md5', '', password)
        return (drupal_user.password == encripted_password)
    else:
        return django_check_password(password, drupal_user.password)


def get_user_data(drupal_user):
    full_name = ''
    if Realname.objects.using(DRUPAL_DB).filter(uid=drupal_user.uid).exists():
        full_name = Realname.objects.using(DRUPAL_DB).get(
            uid=drupal_user.uid).realname
    username = drupal_user.name.replace('@', '-')
    return username, drupal_user.mail, full_name


def migrate(login):
    """Migrates a drupal user given an username or email address."""
    drupal_user = get_user(login)
    if drupal_user:
        username, email, full_name = get_user_data(drupal_user)
        django_user = User(username=username[:30], email=email)
        from users.models import create_profile
        try:
            profile = create_profile(django_user, username=username)
            profile.password = drupal_user.password
            profile.save()
            return profile
        except IntegrityError, ex:
            log.error('migration of %s failed: %s' % (login, ex))
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


class Realname(models.Model):
    uid = models.IntegerField(primary_key=True)
    realname = models.CharField(max_length=765)

    class Meta:
        db_table = u'realname'


class Authmap(models.Model):
    aid = models.IntegerField(primary_key=True)
    uid = models.IntegerField()
    authname = models.CharField(max_length=384)
    module = models.CharField(max_length=384)

    class Meta:
        db_table = u'authmap'


class ContentTypeProfile(models.Model):
    vid = models.IntegerField(primary_key=True)
    nid = models.IntegerField()
    field_profile_country_value = models.TextField(blank=True)
    field_profile_city_value = models.TextField(blank=True)
    field_profile_aboutme_value = models.TextField(blank=True)
    field_profile_aboutme_format = models.IntegerField(null=True, blank=True)
    field_profile_firstname_value = models.TextField(blank=True)
    field_profile_lastname_value = models.TextField(blank=True)
    field_profile_facebook_url = models.CharField(max_length=765, blank=True)
    field_profile_facebook_title = models.CharField(max_length=765, blank=True)
    field_profile_facebook_attributes = models.TextField(blank=True)
    field_profile_twitter_url = models.CharField(max_length=765, blank=True)
    field_profile_twitter_title = models.CharField(max_length=765, blank=True)
    field_profile_twitter_attributes = models.TextField(blank=True)
    field_profile_gender_value = models.TextField(blank=True)
    field_profile_education_value = models.TextField(blank=True)
    field_profile_email_subs_value = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = u'content_type_profile'
