from django.contrib.auth.models import User

from openid.consumer.consumer import SUCCESS
from openid.extensions import ax

from django_openid_auth.auth import OpenIDBackend
from django_openid_auth.models import UserOpenID

from users.auth import ax_attributes
from users.models import UserProfile


class CustomUserBackend(object):
    supports_anonymous_user = False
    supports_object_permissions = False

    def authenticate(self, username=None, password=None):
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
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class CustomOpenIDBackend(OpenIDBackend):
    """
    Custom backend implementation. Create new accounts based on OpenID
    credentials *only* on registration, not on sign in attempts.
    """

    def unique_username(self, nickname):
        """
        Given a base username, determine a unique one by appending an
        incrementing integer to it until it's unique.
        """
        i = 1
        while True:
            username = nickname
            if i > 1:
                username += str(i)
            try:
                User.objects.get(username__exact=username)
            except User.DoesNotExist:
                break
            i += 1
        return username

    def update_user_details_from_ax(self, user, ax_response):
        """
        Update ```user``` and associated ```profile``` object with information
        obtained using OpenID attribute exchange.
        """
        if not ax_response:
            return
        profile = user.get_profile()
        for key, val in ax_attributes.iteritems():
            attr = ax_response.getSingle(val[0])
            if not attr:
                continue
            if key == 'first_name' or key == 'last_name':
                setattr(profile, key, attr)
            elif key == 'username':
                user.username = self.unique_username(attr)
            else:
                setattr(user, key, attr)
        user.save()
        profile.save()

    def update_user_details_from_sreg(self, user, sreg_response):
        """
        Override ```update_user_details_from_sreg``` to update a user profile,
        which will then update the user object using a post_save signal.
        """
        fullname = sreg_response.get('fullname')
        profile = user.get_profile()
        if fullname:
            if ' ' in fullname:
                profile.first_name, profile.last_name = fullname.rsplit(None, 1)
            else:
                profile.first_name = u''
                profile.last_name = fullname
            profile.save()
        email = sreg_response.get('email')
        if email:
            user.email = email
        user.save()

    def authenticate(self, **kwargs):
        """Authenticate a user using an OpenID response."""
        openid_response = kwargs.get('openid_response')

        if openid_response is None:
            return None

        if openid_response.status != SUCCESS:
            return None

        request = kwargs.get('request')

        if request is None:
            return None

        registering = request.GET.get('registration', False)

        try:
            UserOpenID.objects.get(
                claimed_id__exact=openid_response.identity_url)
        except UserOpenID.DoesNotExist:
            if registering:
                user = self.create_user_from_openid(openid_response)
                ax_response = ax.FetchResponse.fromSuccessResponse(openid_response)
                self.update_user_details_from_ax(user, ax_response)

        return OpenIDBackend.authenticate(self, **kwargs)
