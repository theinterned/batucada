from django.db import models
from django.contrib.auth.models import User, get_hexdigest

class PasswordResetToken(models.Model):
    """Store a unique token related to a user account."""
    user = models.ForeignKey(User, unique=True)
    token = models.CharField(max_length=60)

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
        super(PasswordResetToken, self).save(*args, **kwargs)
