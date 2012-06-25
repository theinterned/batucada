from django.db import models

from tasks import SendNotifications

import logging

log = logging.getLogger(__name__)

def send_notifications(user_profiles, subject_template, body_template,
        template_context, reply_token=None):
    """Asynchronously send email notifications to users
    
    user_profiles - the users to send the notification to
    subject_template - the template to use for the subject
    body_template - the template to use for the body
    template_context - the context to use when rendering the template
    reply_token - used to generate reply_to address reply+reply_token@from.org

    If the reply_token is None, it is assumed that the notification cannot
    be replied to
    """
    args = (user_profiles, subject_template, body_template, template_context,
        reply_token,)

    log.debug("sending notification {0}".format(args))
    SendNotifications.apply_async(args)
