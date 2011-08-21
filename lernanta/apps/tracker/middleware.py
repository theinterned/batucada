import datetime
from users.models import UserProfile

class VisitorTrackerMiddlware:
    def process_request(self, request):
        if request.user.is_authenticated():
            now = datetime.datetime.now()
            profile = request.user.get_profile()
            try:
                profile.last_active = now
                profile.save()
            except:
                pass
