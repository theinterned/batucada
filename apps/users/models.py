from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    """
    Basic user profile for now.

    TODO: Make a full list of profile fields.
    """
    user = models.ForeignKey(User, unique=True)
    homepage = models.CharField(max_length=300)
    location = models.CharField(max_length=300)
    bio = models.TextField()
