import datetime
import random
import string
import hashlib
import os

from django.db import models
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.utils.encoding import smart_str
from django.utils.translation import ugettext as _

from taggit.models import GenericTaggedItemBase, Tag
from taggit.managers import TaggableManager


def get_hexdigest(algorithm, salt, raw_password):
    """Generate password hash."""
    return hashlib.new(algorithm, smart_str(salt + raw_password)).hexdigest()


def create_password(algorithm, raw_password):
    """Create salted, hashed password."""
    salt = os.urandom(5).encode('hex')
    hsh = get_hexdigest(algorithm, salt, raw_password)
    return '$'.join((algorithm, salt, hsh))


class ProfileTag(Tag):
    CATEGORY_CHOICES = (
        ('skill', 'Skill'),
        ('interest', 'Interest'),
    )
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)


class TaggedProfile(GenericTaggedItemBase):
    tag = models.ForeignKey(
        ProfileTag, related_name="%(app_label)s_%(class)s_items")

    class Meta:
        verbose_name = "Tagged User Profile"
        verbose_name_plural = "Tagged User Profiles"


class UserProfile(models.Model):
    """Each user gets a profile."""
    username = models.CharField(max_length=255, default='', unique=True)
    display_name = models.CharField(
        max_length=255, default='', null=True, blank=True)
    password = models.CharField(max_length=255, default='')
    email = models.EmailField(unique=True, null=True)
    bio = models.TextField(blank=True, default='')
    image = models.ImageField(
        upload_to='images/profiles/public', default='', blank=True, null=True)
    confirmation_code = models.CharField(
        max_length=255, default='', blank=True)
    location = models.CharField(max_length=255, blank=True, default='')
    created_on = models.DateTimeField(
        auto_now_add=True, default=datetime.date.today())

    user = models.ForeignKey(User, null=True, editable=False, blank=True)
    tags = TaggableManager(through=TaggedProfile)

    def __unicode__(self):
        return '%s: %s' % (self.id, self.display_name or self.username)

    @models.permalink
    def get_absolute_url(self):
        return ('users_profile_view', (), {
            'username': self.username,
        })

    def create_django_user(self):
        """Make a django.contrib.auth.models.User for this UserProfile."""
        self.user = User(id=self.pk)
        self.user.username = self.email
        self.user.password = self.password
        self.user.email = self.email
        self.user.date_joined = self.created_on
        self.user.backend = 'django.contrib.auth.backends.ModelBackend'
        self.user.save()
        self.save()
        return self.user

    def email_confirmation_code(self, url):
        """Send a confirmation email to the user after registering."""
        body = render_to_string('users/emails/registration_confirm.txt', {
            'confirmation_url': url,
        })
        self.user.email_user(_('Complete Registration'), body)

    def image_or_default(self):
        """Return user profile image or a default."""
        if self.image:
            return self.image
        else:
            return 'images/member-missing.png'

    def generate_confirmation_code(self):
        if not self.confirmation_code:
            self.confirmation_code = ''.join(random.sample(string.letters +
                                                           string.digits, 60))
        return self.confirmation_code

    def set_password(self, raw_password, algorithm='sha512'):
        self.password = create_password(algorithm, raw_password)

    def check_password(self, raw_password):
        if '$' not in self.password:
            valid = (get_hexdigest('md5', '', raw_password) == self.password)
            if valid:
                # Upgrade an old password.
                self.set_password(raw_password)
                self.save()
            return valid

        algo, salt, hsh = self.password.split('$')
        return hsh == get_hexdigest(algo, salt, raw_password)

    @property
    def name(self):
        return self.display_name or self.username
