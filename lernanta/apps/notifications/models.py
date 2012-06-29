from django.db import models

from tasks import SendNotifications, PostNotificationResponse

import logging

log = logging.getLogger(__name__)

class ResponseToken(models.model):
    """ Store response tokens and callbacks """

    # Unique token used to route response coming in via email
    response_token = models.CharField(max_length=32, blank=False)

    # URL to call when receiving a response
    response_callback = models.CharField(max_length=255, blank=False)


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

def post_notification_response(token, from_email, text):

    args = (token, from_email, text,)
    PostNotificationResponse.apply_async(args)
