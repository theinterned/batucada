from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save

try:
    from l10n.urlresolvers import reverse
except ImportError:
    from django.core.urlresolvers import reverse

class Status(models.Model):
    author = models.ForeignKey(User)
    object_type = 'http://activitystrea.ms/schema/1.0/status'
    
    status = models.CharField(max_length=1024)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return self.status

    def get_absolute_url(self):
        return reverse('statuses.views.show',
                       kwargs=dict(status_id=self.pk))
    
def status_creation_handler(sender, **kwargs):
    status = kwargs.get('instance', None)
    if not isinstance(status, Status):
        return
    try:
        import activity
        activity.send(status.author, 'post', status)
    except ImportError:
        return

post_save.connect(status_creation_handler, sender=Status)
