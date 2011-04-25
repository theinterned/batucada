from django.http import HttpResponseRedirect
from django.conf import settings

from users.models import UserProfile
from l10n.urlresolvers import reverse


class ProfileExistMiddleware(object):

    def process_request(self, request):
        if request.user.is_authenticated():
            try:
                profile = request.user.get_profile()
            except UserProfile.DoesNotExist:
                dashboard_url = reverse('dashboard_index')      
                if request.path in (dashboard_url, reverse('users_profile_create')):
                    return None
                for prefix in settings.NO_PROFILE_URLS:
                    if request.path.startswith(prefix):
                        return None
                return HttpResponseRedirect(dashboard_url)
            
