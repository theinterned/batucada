from django.db import models

from tasks import SendNotifications

def send_notifications(user_profiles, subject_template, body_template,
        template_context, reply_token=None):
    """Asynchronously send email notifications to users
    
    user_profiles - the users to send the notification to
    subject_template - the template to use for the subject
    body_template - the template to use for the body
    template_context - the context to use when rendering the template
    reply_token - used to generate reply_to address reply+reply_token@from.org
    """
    args = (user_profiles, subject_template, body_template, template_context)
    SendNotifications.apply_async(args)
