from django.db.models.signals import post_save

from messages.models import Message
from users.tasks import SendUserEmail
from preferences.models import AccountPreferences

import logging

log = logging.getLogger(__name__)


def message_sent_handler(sender, **kwargs):
    message = kwargs.get('instance', None)
    if not isinstance(message, Message):
        return
    user = message.recipient
    preferences = AccountPreferences.objects.filter(
        user=user.get_profile())
    for preference in preferences:
        if preference.value and preference.key == 'no_email_message_received':
            return
    subject = 'Private Message from %s' % (message.sender.get_profile().name,)
    body = ""  # todo - write some copy for this
    SendUserEmail.apply_async((user.get_profile(), subject, body))
post_save.connect(message_sent_handler, sender=Message)
