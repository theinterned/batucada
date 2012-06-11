from django.db import models

from tasks import SendNotifications

def send_notifications(user_profiles, subject_template, body_template, context):
    """ Asynchronously send email notifications to users """
    SendNotifications.apply_async(
        (user_profiles, subject_template, body_template, context))
