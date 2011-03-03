import logging

from django.contrib.auth.models import User

from users.models import UserProfile
from users import drupal

log = logging.getLogger(__name__)


class CustomUserBackend(object):
    supports_anonymous_user = False
    supports_object_permissions = False

    def authenticate(self, username=None, password=None):
        log.debug("Attempting to authenticate user %s" % (username,))
        try:
            if '@' in username:
                profile = UserProfile.objects.get(email=username)
            else:
                profile = UserProfile.objects.get(username=username)
            if profile.check_password(password):
                if profile.user is None:
                    profile.create_django_user()
                return profile.user
        except UserProfile.DoesNotExist:
            log.debug("User does not exist: %s" % (username,))
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

class DrupalUserBackend(object):
    supports_object_permissions = False
    supports_anonymous_user = False
    supports_inactive_user = False

    def authenticate(self, username=None, password=None):
        log.debug("Attempting to authenticate drupal user %s" % (username,))
        drupal_user = drupal.get_user(username)
        if drupal_user:
            try:
                profile = UserProfile.objects.get(username=drupal_user.name)
                log.debug("Drupal user resgistered already: %s" % (username,))
                return None
            except UserProfile.DoesNotExist:
                if drupal.check_password(drupal_user, password):
                    user_data = drupal.get_user_data(drupal_user)
                    profile = UserProfile(**user_data)
                    profile.set_password(password)
                    profile.save()
                    if profile.user is None:
                        profile.create_django_user()
                    return profile.user
        else:
            log.debug("Drupal user does not exist: %s" % (username,))
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
