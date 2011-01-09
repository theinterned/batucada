import logging

from django.contrib.auth.models import User

from users.models import UserProfile

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
