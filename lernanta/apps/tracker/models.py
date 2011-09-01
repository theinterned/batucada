from django.contrib.auth.models import User
from django.db import models


class PageView(models.Model):
    session_key = models.CharField(max_length=100, db_index=True)
    user = models.ForeignKey(User, null=True, blank=True)
    access_time = models.DateTimeField(auto_now_add=True, db_index=True)
    request_url = models.CharField(max_length=755, db_index=True)
    referrer_url = models.URLField(
                         verify_exists=False,
                         db_index=True,
                         blank=True, null=True)
    ip_address = models.IPAddressField(
                         blank=True, null=True)
    time_on_page = models.IntegerField(blank=True, null=True)

    def __repr__(self):
        return '<Session: key %s, access time %s, request_url %s, time_on_page %s, user %s>' \
                % (self.session_key, self.access_time, self.request_url, self.time_on_page, self.user)