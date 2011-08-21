from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.db import models


class PageView(models.Model):
    session_key = models.CharField(max_length=100)
    user = models.ForeignKey(User, null=True, blank=True)
    access_time = models.DateTimeField(auto_now_add=True, db_index=True)
    request_url = models.CharField(max_length=755, db_index=True)
    referrer_url = models.URLField(
                         verify_exists=False,
                         db_index=True,
                         blank=True, null=True)
    ip_address = models.IPAddressField(
                         blank=True, null=True)
