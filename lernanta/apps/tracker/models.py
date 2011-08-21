
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.db import models

class Visitor(models.Model):
    session = models.OneToOneField(Session, db_index=True,null=True,blank=True,primary_key=True)
    user = models.ForeignKey(User, null=True, blank=True)
    session_start = models.DateTimeField(help_text="Date Request started processing", auto_now_add=True, db_index=True)
    #stats = VisitorActivityManager()
    request_url = models.CharField(max_length=755,db_index=True)
    referrer_url = models.URLField(
                         verify_exists=False,
                         db_index=True,
                         blank=True, null=True)
    ip_address = models.IPAddressField(
                         blank=True,null=True)


# VisitorManager?