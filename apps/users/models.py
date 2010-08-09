import hashlib

from django.db import models
from django.contrib.auth.models import User, get_hexdigest

class Profile(models.Model):
    """User profile."""
    user = models.ForeignKey(User, unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    location = models.CharField(max_length=255)
    image = models.CharField(max_length=255)
    bio = models.TextField()

class ProfilePhoneNumber(models.Model):
    """A user can store multiple phone numbers in their profile."""
    profile = models.ForeignKey(Profile)
    number = models.CharField(max_length=25)
    label = models.CharField(max_length=20)

class ProfileLink(models.Model):
    """A user profile can have zero or more links associated with it."""
    profile = models.ForeignKey(Profile)
    title = models.CharField(max_length=50)
    uri = models.CharField(max_length=320)

class ProfileSkill(models.Model):
    """A user profile can have zero or more skills."""
    profile = models.ForeignKey(Profile)
    name = models.CharField(max_length=30)

class ProfileInterest(models.Model):
    """A user profile can have zero or more interests."""
    profile = models.ForeignKey(Profile)
    name = models.CharField(max_length=30)

class ConfirmationToken(models.Model):
    """Store a unique token related to a user account."""
    user = models.ForeignKey(User, unique=True)
    token = models.CharField(max_length=60)
    plaintext = ""

    def __unicode__(self):
        return '%s,%s' % (self.user.username, self.token)

    def _hash_token(self, raw_token):
        import random
        algo = 'sha1'
        salt = get_hexdigest(algo, str(random.random()),
                             str(random.random()))[:5]
        hsh = get_hexdigest(algo, salt, raw_token)
        return '%s$%s$%s' % (algo, salt, hsh)

    def check_token(self, raw_token):
        algo, salt, hsh = self.token.split('$')
        return hsh == get_hexdigest(algo, salt, raw_token)

    def save(self, *args, **kwargs):
        self.token = self._hash_token(self.token)
        super(ConfirmationToken, self).save(*args, **kwargs)

def unique_confirmation_token(user, length=32):
    """Create a confirmation token for the given user, deleting existing."""
    ConfirmationToken.objects.filter(user__exact=user.id).delete()
    plaintext = User.objects.make_random_password(length=length)
    token = ConfirmationToken(
        user=user,
        token=plaintext
    )
    token.plaintext = plaintext
    token.save()
    return token
