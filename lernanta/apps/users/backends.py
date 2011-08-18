import logging

from django.contrib.auth.models import User
from django.db import IntegrityError

from users.models import UserProfile, create_profile
from users import drupal
from django_openid_auth.auth import OpenIDBackend, SUCCESS
from django_openid_auth.models import UserOpenID

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
                return profile.user
        except UserProfile.DoesNotExist:
            log.debug("Profile does not exist: %s" % (username,))
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class DrupalUserBackend(CustomUserBackend):

    def authenticate(self, username=None, password=None):
        log.debug("Attempting to authenticate drupal user %s" % (username,))
        drupal_user = drupal.get_user(username)
        if drupal_user:
            try:
                profile = UserProfile.objects.get(username=drupal_user.name)
                log.debug("Drupal user already resgistered: %s" % (username,))
                return None
            except UserProfile.DoesNotExist:
                if drupal.check_password(drupal_user, password):
                    username, email, full_name = drupal.get_user_data(
                        drupal_user)
                    try:
                        django_user = User(username=username[:30], email=email)
                        profile = create_profile(django_user,
                            username=username)
                        profile.full_name = full_name
                        profile.set_password(password)
                        profile.save()
                        return profile.user
                    except IntegrityError:
                        return None
        else:
            log.debug("Drupal user does not exist: %s" % (username,))
            return None


class DrupalOpenIDBackend(OpenIDBackend):

    def authenticate(self, **kwargs):
        """Authenticate the user based on an OpenID response."""
        # Require that the OpenID response be passed in as a keyword
        # argument, to make sure we don't match the username/password
        # calling conventions of authenticate.

        openid_response = kwargs.get('openid_response')
        if openid_response is None:
            return None

        if openid_response.status != SUCCESS:
            return None
        msg = 'Attempting to authenticate drupal user %s'
        log.debug(msg % openid_response.identity_url)

        try:
            UserOpenID.objects.get(
                claimed_id__exact=openid_response.identity_url)
            msg = 'Drupal openid user resgistered already: %s'
            log.debug(msg % openid_response.identity_url)
            return None
        except UserOpenID.DoesNotExist:
            drupal_user = drupal.get_openid_user(openid_response.identity_url)
            if drupal_user:
                username, email, full_name = drupal.get_user_data(drupal_user)
                try:
                    django_user = User(username=username[:30], email=email)
                    profile = create_profile(django_user, username=username)
                    profile.full_name = full_name
                    profile.save()
                    self.associate_openid(django_user, openid_response)
                    return django_user
                except IntegrityError:
                    return None
        return None
