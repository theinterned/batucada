from django.db import models
from django.contrib.auth.models import User

def authenticate(username=None, password=None):
    """
    Allow model backed user objects to support authentication by
    email / password as well as username / password.
    """
    backend = 'django.contrib.auth.backends.ModelBackend'
    try:
        if '@' in username:
            kwargs = dict(email=username)
        else:
            kwargs = dict(username=username)
        user = User.objects.get(**kwargs)
        if user.check_password(password):
            user.backend = backend
            return user
    except User.DoesNotExist:
        return None

class Profile(models.Model):
    """
    Basic user profile for now.

    TODO: Make a full list of profile fields.
    """
    user = models.ForeignKey(User, unique=True)
    homepage = models.CharField(max_length=300)
    location = models.CharField(max_length=300)
    bio = models.TextField()
