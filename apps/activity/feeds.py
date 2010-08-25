from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed

from activity.models import Activity

class ActivityStreamAtomFeedGenerator(Atom1Feed):
    """Tweaks to Atom feed generator to include Activity Stream data."""
    pass

class UserActivityFeed(Feed):
    feed_type = ActivityStreamAtomFeedGenerator
    title = "Activity Stream Example"
    link = "/foo/"
    description = "Placeholder"
    
    def items(self):
        """Obviously a placeholder."""
        return Activity.objects.all()

class ObjectActivityFeed(Feed):
    feed_type = ActivityStreamAtomFeedGenerator
    title = "Activity Stream Example"
    link = "/foo/"
    description = "Placeholder"
    
    def items(self):
        """Obviously a placeholder."""
        return Activity.objects.all()
