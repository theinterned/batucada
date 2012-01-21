from django.http import HttpResponseRedirect
from django.conf import settings

from users.models import UserProfile
from l10n.urlresolvers import reverse


class ProfileExistMiddleware(object):

    def process_request(self, request):
        if request.user.is_authenticated():
            try:
                request.user.get_profile()
            except UserProfile.DoesNotExist:
                dashboard_url = reverse('dashboard')
                profile_create_url = reverse('users_profile_create')
                logout_url = reverse('users_logout')
                check_username_url = reverse('users_check_username')
                valid_urls = (dashboard_url, profile_create_url, logout_url, check_username_url)
                if request.path in valid_urls:
                    return None
                for prefix in settings.NO_PROFILE_URLS:
                    if request.path.startswith(prefix):
                        return None
                return HttpResponseRedirect(dashboard_url)
